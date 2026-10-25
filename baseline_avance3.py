"""Baseline anual municipal: fuentes verificables, ajuste temporal y Ridge simple."""
from pathlib import Path
import io, json, re, hashlib, zipfile, unicodedata
import numpy as np
import pandas as pd
import pdfplumber
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score, mean_squared_log_error
from fe_avance2 import read_raw, prepare_panel, build_features, NUMERIC

STATE_NAMES=['Aguascalientes','Baja California','Baja California Sur','Campeche','Coahuila','Colima',
             'Chiapas','Chihuahua','Ciudad de México','Durango','Guanajuato','Guerrero','Hidalgo',
             'Jalisco','Estado de México','Michoacán','Morelos','Nayarit','Nuevo León','Oaxaca','Puebla',
             'Querétaro','Quintana Roo','San Luis Potosí','Sinaloa','Sonora','Tabasco','Tamaulipas',
             'Tlaxcala','Veracruz','Yucatán','Zacatecas']
MONTHS=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
CORE=['produccion_lag2','cosechada_lag2','sembrada_lag2','rendimiento_lag2',
      'cambio_log_produccion','cv_produccion_3']
MACRO=['inflacion_usa_lag2','depreciacion_mxn_lag2','oferta_x_inflacion','oferta_x_depreciacion']
CLIMATE=['temperatura_estado_lag2','amplitud_mensual_lag2','cambio_temperatura_lag2','oferta_x_cambio_temperatura']
EXTERNAL=MACRO+CLIMATE
VARIANTS={'Ridge nivel':['produccion_lag2'],'Ridge capacidad':CORE,
          'Ridge con externos':CORE+EXTERNAL,'Ridge atributos A2':NUMERIC}
GROUPS={'Escala y capacidad':['produccion_lag2','cosechada_lag2','sembrada_lag2'],
        'Productividad':['rendimiento_lag2'],'Dinámica y variabilidad':['cambio_log_produccion','cv_produccion_3'],
        'Macroeconomía':MACRO,'Clima estatal':CLIMATE}

def normalize(name):
    return ''.join(c for c in unicodedata.normalize('NFD',name) if unicodedata.category(c)!='Mn').lower().strip()

def verify_external_files(root):
    root=Path(root)
    macro_records=json.loads((root/'proveniencia_externos.json').read_text())
    for item in macro_records:
        assert hashlib.sha256((root/item['archivo']).read_bytes()).hexdigest()==item['sha256']
    climate_records=json.loads((root/'proveniencia_smn.json').read_text())
    with zipfile.ZipFile(root/'smn_temperatura_fuentes.zip') as z:
        assert len(z.namelist())==21
        for item in climate_records:
            assert hashlib.sha256(z.read(item['archivo'])).hexdigest()==item['sha256']
    return macro_records,climate_records

def extract_temperature(root):
    """Extrae 12 meses + anual publicado; no calcula el anual promediando estados."""
    root=Path(root)
    names={normalize(s):str(i+1).zfill(2) for i,s in enumerate(STATE_NAMES)}
    names.update({'distrito federal':'09','mexico':'15'})
    rows=[];audit=[]
    with zipfile.ZipFile(root/'smn_temperatura_fuentes.zip') as z:
        for filename in sorted(z.namelist()):
            year=int(re.search(r'(\d{4})',filename).group())
            with pdfplumber.open(io.BytesIO(z.read(filename))) as pdf:
                assert len(pdf.pages)==1
                text=pdf.pages[0].extract_text()
            printed_years=re.findall(r'\b(?:19|20)\d{2}\b',' '.join(text.splitlines()[:3]))
            assert len(printed_years)==1,(filename,printed_years)
            if int(printed_years[0])!=year:
                # Se conserva el PDF original y se pone en cuarentena este año.
                # No se reasignan sus valores a 2012 ni se acepta el nombre como prueba.
                assert year==2013 and printed_years[0]=='2012',(filename,printed_years)
                audit.append({'archivo':filename,'anio_nombre':year,'anio_impreso':int(printed_years[0]),
                              'decision':'Cuarentena: año interno distinto del nombre','filas_utilizadas':0})
                continue
            count=0
            for line in text.splitlines():
                pieces=line.split()
                if len(pieces)<14:
                    continue
                values=pieces[-13:]
                if not all(re.fullmatch(r'-?\d+(?:\.\d+)?',p) for p in values):
                    continue
                name=' '.join(pieces[:-13]); normalized=normalize(name)
                if normalized=='nacional':
                    code='00'
                else:
                    assert normalized in names,(filename,name)
                    code=names[normalized]
                row={'anio_medicion':year,'estado':code,'entidad_smn':name,
                     **dict(zip(MONTHS+["anual_c"],map(float,values))),'fuente_pdf':filename}
                rows.append(row);count+=1
            assert count==33,(filename,count)
            audit.append({'archivo':filename,'anio_nombre':year,'anio_impreso':int(printed_years[0]),
                          'decision':'Aceptado','filas_utilizadas':count})
    result=pd.DataFrame(rows)
    assert len(result)==20*33 and not result.duplicated(['anio_medicion','estado']).any()
    assert 2013 not in result.anio_medicion.unique()
    assert result[MONTHS+['anual_c']].apply(lambda s:s.between(-10,50)).all().all()
    result.attrs['auditoria']=audit
    return result

def extract_macro(root):
    root=Path(root)
    data={}
    for name,column in [('inflacion_usa','inflacion_usa_pct'),('tipo_cambio_mex','mxn_por_usd')]:
        obj=json.loads((root/(name+'.json')).read_text())
        assert len(obj[1])==24
        data[column]=pd.Series({int(r['date']):r['value'] for r in obj[1]},name=column,dtype=float)
    out=pd.concat(data.values(),axis=1).sort_index().rename_axis('anio_medicion').reset_index()
    assert out.notna().all().all() and out.mxn_por_usd.gt(0).all()
    assert not out.anio_medicion.duplicated().any()
    return out

def integrate_sources(root):
    root=Path(root)
    verify_external_files(root/'data/externos')
    raw=read_raw(root/'data/raw/siap_produccion.csv')
    panel,historical,quarantine=prepare_panel(raw)
    all_features=build_features(panel)
    # Incluir todos los objetivos disponibles desde 2007 para crear ventanas de ajuste.
    f=all_features.loc[all_features.observado_objetivo & all_features.con_historia_minima & all_features.anio.ge(2007)].copy()
    f['estado']=f.cvegeo.str[:2]
    temperature=extract_temperature(root/'data/externos')
    macro=extract_macro(root/'data/externos')
    for lag in [2,3]:
        m=macro.copy().rename(columns={'anio_medicion':'anio'})
        m['anio']+=lag
        m=m.rename(columns={c:c+f'_t{lag}' for c in m if c!='anio'})
        f=f.merge(m,on='anio',how='left',validate='many_to_one')
        climate=temperature.loc[temperature.estado.ne('00')].copy()
        climate['amplitud_mensual']=climate[MONTHS].max(axis=1)-climate[MONTHS].min(axis=1)
        climate=climate[['estado','anio_medicion','anual_c','amplitud_mensual']].rename(columns={'anio_medicion':'anio'})
        climate['anio']+=lag
        climate=climate.rename(columns={'anual_c':f'anual_c_t{lag}','amplitud_mensual':f'amplitud_t{lag}'})
        f=f.merge(climate,on=['estado','anio'],how='left',validate='many_to_one')
    f['inflacion_usa_lag2']=f.inflacion_usa_pct_t2
    f['depreciacion_mxn_lag2']=100*(f.mxn_por_usd_t2/f.mxn_por_usd_t3-1)
    f['temperatura_estado_lag2']=f.anual_c_t2
    f['amplitud_mensual_lag2']=f.amplitud_t2
    f['cambio_temperatura_lag2']=f.anual_c_t2-f.anual_c_t3
    f['oferta_x_inflacion']=f.produccion_lag2*f.inflacion_usa_lag2/100
    f['oferta_x_depreciacion']=f.produccion_lag2*f.depreciacion_mxn_lag2/100
    f['oferta_x_cambio_temperatura']=f.produccion_lag2*f.cambio_temperatura_lag2
    f=f.sort_values(['anio','cvegeo']).reset_index(drop=True)
    assert not f.duplicated(['anio','cvegeo']).any()
    assert f[MACRO].notna().all().all(),'Falla cobertura macroeconómica.'
    expected_years={2015,2016} # t-2 o t-3 coincide con el PDF 2013 en cuarentena.
    missing_climate=f[CLIMATE].isna().any(axis=1)
    assert set(f.loc[missing_climate,'anio'].unique())==expected_years
    return raw,panel,f,temperature,macro,historical,quarantine

class RidgeBaseline:
    """Ridge alpha=1; imputación/escalamiento/filtro ajustados dentro de cada ventana.

    La versión de nivel usa un coeficiente y origen cero; conserva unidades y no
    necesita intercepto global. Las variantes multivariadas incluyen intercepto.
    """
    def __init__(self,columns,alpha=1.0,level_only=False):
        self.columns=list(columns);self.alpha=alpha;self.level_only=level_only

    def fit(self,frame):
        self.train_end_=int(frame.anio.max())
        self.train_start_=int(frame.anio.min())
        self.n_train_=len(frame)
        self.imputer_=SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True)
        x=self.imputer_.fit_transform(frame[self.columns])
        self.names_before_=self.imputer_.get_feature_names_out(self.columns).tolist()
        self.variance_=VarianceThreshold(0).fit(x)
        self.names_=np.array(self.names_before_)[self.variance_.get_support()].tolist()
        self.scaler_=StandardScaler(with_mean=not self.level_only).fit(self.variance_.transform(x))
        z=self.scaler_.transform(self.variance_.transform(x))
        self.model_=Ridge(alpha=self.alpha,fit_intercept=not self.level_only,solver='svd').fit(z,frame.produccion_t)
        self.n_features_=z.shape[1]
        return self

    def matrix(self,frame):
        x=self.imputer_.transform(frame[self.columns])
        return self.scaler_.transform(self.variance_.transform(x))

    def predict_raw(self,frame):
        return self.model_.predict(self.matrix(frame))

    def predict(self,frame):
        return np.maximum(0,self.predict_raw(frame))

    def coefficients(self):
        slopes=self.model_.coef_/self.scaler_.scale_
        means=self.scaler_.mean_ if self.scaler_.with_mean else np.zeros(len(slopes))
        intercept=float(self.model_.intercept_-np.dot(slopes,means))
        out=pd.DataFrame({'variable':self.names_,'coeficiente_estandarizado_t':self.model_.coef_,
                          'coeficiente_unidad_original':slopes,'escala_train':self.scaler_.scale_})
        return out,intercept

def metrics(y,p):
    y,p=np.asarray(y,dtype=float),np.asarray(p,dtype=float)
    assert np.isfinite(p).all() and (p>=0).all()
    error=p-y
    return {'n':len(y),'MAE_t':mean_absolute_error(y,p),'RMSE_t':root_mean_squared_error(y,p),
            'WAPE_pct':100*np.abs(error).sum()/y.sum() if y.sum()>0 else np.nan,
            'sesgo_t':error.mean(),'sesgo_pct':100*error.sum()/y.sum() if y.sum()>0 else np.nan,
            'R2':r2_score(y,p) if len(y)>1 and np.var(y)>0 else np.nan,
            'RMSLE':np.sqrt(mean_squared_log_error(y,p))}

def make_model(name,columns=None):
    return RidgeBaseline(VARIANTS[name] if columns is None else columns,alpha=1.0,level_only=name=='Ridge nivel')

def temporal_validation(frame,years=(2018,2019,2020)):
    records,diagnostics=[],[]
    for year in years:
        train=frame.loc[frame.anio.between(2007,year-3)]
        val=frame.loc[frame.anio.eq(year)]
        assert train.anio.max()<=year-3 and val.anio.eq(year).all()
        for name in ['Mediana global','Persistencia t-2']+list(VARIANTS):
            if name=='Mediana global':
                pred=np.full(len(val),train.produccion_t.median());n_columns=0
            elif name=='Persistencia t-2':
                pred=val.produccion_lag2.to_numpy();n_columns=1
            else:
                model=make_model(name).fit(train);pred=model.predict(val);n_columns=model.n_features_
            record=val[['cvegeo','estado','anio','produccion_t','produccion_lag2']].copy()
            record['modelo']=name;record['prediccion_t']=pred
            record['fin_train']=int(train.anio.max())
            records.append(record)
            diagnostics.append({'modelo':name,'anio_validacion':year,'n_train':len(train),'fin_train':int(train.anio.max()),
                                'columnas':n_columns,**metrics(val.produccion_t,pred)})
    predictions=pd.concat(records,ignore_index=True)
    summary=pd.DataFrame([{'modelo':name,**metrics(d.produccion_t,d.prediccion_t)} for name,d in predictions.groupby('modelo',sort=False)])
    return predictions,pd.DataFrame(diagnostics),summary

def ablate_groups(frame,reference_name='Ridge con externos'):
    """Wrapper: retirar un bloque, reajustar desde cero y medir sobre validación temporal."""
    rows=[]
    groups=GROUPS
    for year in [2018,2019,2020]:
        train=frame[frame.anio.between(2007,year-3)]
        val=frame[frame.anio.eq(year)]
        full=make_model(reference_name).fit(train)
        full_error=np.abs(full.predict(val)-val.produccion_t).sum()
        for group,cols in groups.items():
            kept=[c for c in VARIANTS[reference_name] if c not in cols]
            # Las interacciones de oferta no deben sobrevivir sin su componente principal.
            if group=='Escala y capacidad':
                kept=[c for c in kept if not c.startswith('oferta_x_')]
            reduced=make_model(reference_name,columns=kept).fit(train)
            error=np.abs(reduced.predict(val)-val.produccion_t).sum()
            rows.append({'grupo_retirado':group,'anio':year,'n_validacion':len(val),
                         'suma_error_modelo_completo':full_error,'suma_error_sin_grupo':error,
                         'columnas_sin_grupo':reduced.n_features_})
    detail=pd.DataFrame(rows)
    summary=detail.groupby('grupo_retirado',as_index=False).agg(n=('n_validacion','sum'),
        error_completo=('suma_error_modelo_completo','sum'),error_sin_grupo=('suma_error_sin_grupo','sum'))
    summary['MAE_completo_t']=summary.error_completo/summary.n
    summary['MAE_sin_grupo_t']=summary.error_sin_grupo/summary.n
    summary['delta_MAE_t']=summary.MAE_sin_grupo_t-summary.MAE_completo_t
    summary['delta_MAE_pct']=100*summary.delta_MAE_t/summary.MAE_completo_t
    return detail,summary.sort_values('delta_MAE_t',ascending=False)

def paired_bootstrap(y,model,persistence,n_boot=1500,seed=42):
    """Sensibilidad condicional a los municipios de un año, no a nuevos años."""
    rng=np.random.default_rng(seed)
    y,model,persistence=map(np.asarray,[y,model,persistence])
    e_model=np.abs(y-model);e_reference=np.abs(y-persistence)
    idx=rng.integers(0,len(y),size=(n_boot,len(y)))
    skills=1-e_model[idx].mean(axis=1)/e_reference[idx].mean(axis=1)
    return {'n_replicas':n_boot,'semilla':seed,'skill_puntual':1-e_model.mean()/e_reference.mean(),
            'percentil_2_5':float(np.quantile(skills,.025)),'percentil_97_5':float(np.quantile(skills,.975))}

def state_bootstrap(frame,pred,persistence,n_boot=1500,seed=42):
    """Pares re-muestreados por estado para sensibilidad a dependencia territorial."""
    d=frame[['estado','produccion_t']].copy()
    d['error_modelo']=np.abs(d.produccion_t-np.asarray(pred))
    d['error_referencia']=np.abs(d.produccion_t-np.asarray(persistence))
    by=d.groupby('estado')[['error_modelo','error_referencia']].sum()
    rng=np.random.default_rng(seed)
    idx=rng.integers(0,len(by),size=(n_boot,len(by)))
    s=1-by.error_modelo.to_numpy()[idx].sum(axis=1)/by.error_referencia.to_numpy()[idx].sum(axis=1)
    return {'n_replicas':n_boot,'semilla':seed,'estados':len(by),
            'skill_puntual':1-by.error_modelo.sum()/by.error_referencia.sum(),
            'percentil_2_5':float(np.quantile(s,.025)),'percentil_97_5':float(np.quantile(s,.975))}

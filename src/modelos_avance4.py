"""Modelos individuales: comparación temporal, búsqueda reproducible y elección.

Cada objeto ajusta un único regresor. Imputación, escalamiento y selección de
columnas son preparación de datos; no se agregan predicciones de varios modelos.
"""
from pathlib import Path
from itertools import product
import json, time, hashlib, warnings
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import VarianceThreshold
from sklearn.linear_model import ElasticNet, HuberRegressor, QuantileRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.exceptions import ConvergenceWarning
from baseline_avance3 import integrate_sources, make_model as make_baseline, metrics, CORE, CLIMATE, EXTERNAL

ALGORITHMS=['ElasticNet','Huber','Cuantil','CART','KNN','SVR','MLP']
LOGS=['log_produccion_lag2','log_cosechada_lag2','log_sembrada_lag2']
FEATURE_SETS={'nivel':['produccion_lag2'],'capacidad':list(CORE),
              'agro_clima':list(CORE)+list(CLIMATE),'completo':list(CORE)+list(EXTERNAL)+LOGS}
PHASE_YEARS={'ranking':(2015,2016,2017),'ajuste':(2018,2019,2020),'confirmacion':(2021,2022)}
SIMPLICITY={'ElasticNet':1,'Huber':1,'Cuantil':1,'CART':2,'KNN':3,'SVR':4,'MLP':5}
DEFAULTS={
 'ElasticNet':{'features':'completo','alpha':.001,'l1_ratio':.5},
 'Huber':{'features':'completo','epsilon':1.35,'alpha':.0001},
 'Cuantil':{'features':'completo','alpha':.001},
 'CART':{'features':'completo','max_depth':6,'min_samples_leaf':10,'ccp_alpha':0.0},
 'KNN':{'features':'completo','n_neighbors':9,'weights':'distance','p':2},
 'SVR':{'features':'completo','C':10.0,'epsilon':.01,'gamma':'scale','kernel':'rbf'},
 'MLP':{'features':'completo','hidden_layer_sizes':[32],'activation':'relu','alpha':.001,'learning_rate_init':.001}}

def canonical(config):
    return json.dumps(config,sort_keys=True,ensure_ascii=False,separators=(',',':'))

def config_id(name,config):
    return hashlib.sha256((name+canonical(config)).encode()).hexdigest()[:12]

def load_frame(root):
    raw,panel,f,temp,macro,history,quarantine=integrate_sources(Path(root))
    f=f.copy()
    for new,old in zip(LOGS,['produccion_lag2','cosechada_lag2','sembrada_lag2']):
        f[new]=np.log1p(f[old])
    return raw,panel,f,temp,macro,history,quarantine

def estimator(name,config):
    params={k:v for k,v in config.items() if k!='features'}
    if name=='ElasticNet':
        return ElasticNet(**params,max_iter=50000,tol=1e-5,selection='cyclic')
    if name=='Huber':
        return HuberRegressor(**params,max_iter=6000,tol=1e-6)
    if name=='Cuantil':
        return QuantileRegressor(**params,quantile=.5,solver='highs')
    if name=='CART':
        return DecisionTreeRegressor(**params,criterion='squared_error',random_state=42)
    if name=='KNN':
        return KNeighborsRegressor(**params,algorithm='auto',n_jobs=1)
    if name=='SVR':
        return SVR(**params,cache_size=256,max_iter=1000000,tol=1e-3)
    if name=='MLP':
        return MLPRegressor(**params,solver='adam',max_iter=1500,tol=1e-4,
                            n_iter_no_change=30,early_stopping=False,random_state=42)
    raise ValueError(name)

class IndividualModel:
    def __init__(self,name,config=None):
        self.name=name
        self.config=dict(DEFAULTS[name] if config is None else config)
        self.columns=list(FEATURE_SETS[self.config['features']])

    def fit(self,frame):
        started=time.perf_counter()
        self.train_end_=int(frame.anio.max());self.n_train_=len(frame)
        x=frame[self.columns].to_numpy(dtype=float)
        self.imputer_=SimpleImputer(strategy='median',keep_empty_features=True)
        imputed=self.imputer_.fit_transform(x)
        full=np.c_[imputed,np.isnan(x).astype(float)]
        self.names_before_=self.columns+['falta_'+c for c in self.columns]
        self.variance_=VarianceThreshold(0).fit(full)
        self.names_=np.array(self.names_before_)[self.variance_.get_support()].tolist()
        self.scaler_=StandardScaler().fit(self.variance_.transform(full))
        z=self.scaler_.transform(self.variance_.transform(full))
        self.y_scaler_=StandardScaler().fit(frame[['produccion_t']])
        y=self.y_scaler_.transform(frame[['produccion_t']]).ravel()
        self.preparation_s_=time.perf_counter()-started
        self.estimator_=estimator(self.name,self.config)
        assert not self.estimator_.__class__.__module__.startswith('sklearn.ensemble')
        self.fit_messages_=[];self.retry_=False
        start_fit=time.perf_counter()
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter('always')
            self.estimator_.fit(z,y)
        final_warnings=[w for w in captured if issubclass(w.category,ConvergenceWarning)]
        self.fit_messages_=[str(w.message) for w in captured]
        if final_warnings and self.name in {'Huber','ElasticNet','MLP'}:
            # Aumentar únicamente presupuesto numérico; no consultar validación.
            self.retry_=True
            budget=min(int(self.estimator_.max_iter)*3,150000)
            self.estimator_=estimator(self.name,self.config).set_params(max_iter=budget)
            with warnings.catch_warnings(record=True) as retried:
                warnings.simplefilter('always')
                self.estimator_.fit(z,y)
            final_warnings=[w for w in retried if issubclass(w.category,ConvergenceWarning)]
            self.fit_messages_ += [str(w.message) for w in retried]
        self.converged_=not bool(final_warnings)
        self.fit_s_=time.perf_counter()-start_fit
        self.fit_total_s_=self.preparation_s_+self.fit_s_
        self.n_features_=z.shape[1]
        self.iterations_=int(np.max(np.atleast_1d(getattr(self.estimator_,'n_iter_',0))))
        return self

    def matrix(self,frame):
        x=frame[self.columns].to_numpy(dtype=float)
        full=np.c_[self.imputer_.transform(x),np.isnan(x).astype(float)]
        return self.scaler_.transform(self.variance_.transform(full))

    def predict_raw(self,frame):
        scaled=self.estimator_.predict(self.matrix(frame))
        return self.y_scaler_.inverse_transform(np.asarray(scaled).reshape(-1,1)).ravel()

    def predict(self,frame):
        return np.maximum(0,self.predict_raw(frame))

    def diagnostic(self):
        return {'clase':self.estimator_.__class__.__name__,'modulo':self.estimator_.__class__.__module__,
                'columnas_efectivas':self.n_features_,'convergencia':self.converged_,
                'reintento_presupuesto':self.retry_,'iteraciones':self.iterations_,
                'advertencias':self.fit_messages_}

def cv_evaluate(frame,name,config=None,phase='ranking',keep_predictions=False):
    assert phase in PHASE_YEARS
    records=[];folds=[];truth=[];estimated=[]
    for year in PHASE_YEARS[phase]:
        train=frame.loc[frame.anio.between(2007,year-3)]
        val=frame.loc[frame.anio.eq(year)]
        assert train.anio.max()<=year-3 and year not in [2023,2025]
        if name=='Persistencia t-2':
            pred=val.produccion_lag2.to_numpy();fit_s=0.0;prepare_s=0.0;pred_s=0.0
            diag={'columnas_efectivas':1,'convergencia':True,'reintento_presupuesto':False,'iteraciones':0,'advertencias':[]}
            raw_pred=pred
        elif name=='Ridge A3':
            started=time.perf_counter();model=make_baseline('Ridge nivel').fit(train)
            fit_s=time.perf_counter()-started;prepare_s=0.0
            started=time.perf_counter();raw_pred=model.predict_raw(val);pred=np.maximum(0,raw_pred);pred_s=time.perf_counter()-started
            diag={'columnas_efectivas':model.n_features_,'convergencia':True,'reintento_presupuesto':False,'iteraciones':0,'advertencias':[]}
        else:
            model=IndividualModel(name,config).fit(train)
            started=time.perf_counter();raw_pred=model.predict_raw(val);pred=np.maximum(0,raw_pred);pred_s=time.perf_counter()-started
            fit_s=model.fit_s_;prepare_s=model.preparation_s_;diag=model.diagnostic()
        if not np.isfinite(pred).all():raise ValueError(f'Predicción no finita: {name}, {year}')
        truth.extend(val.produccion_t.to_numpy());estimated.extend(pred)
        folds.append({'algoritmo':name,'fase':phase,'anio':year,'n_train':len(train),'fin_train':int(train.anio.max()),
                      **metrics(val.produccion_t,pred),'preparacion_s':prepare_s,'ajuste_estimador_s':fit_s,
                      'entrenamiento_total_s':fit_s+prepare_s,'prediccion_s':pred_s,
                      'negativas_limitadas':int((raw_pred<0).sum()),**diag})
        if keep_predictions:
            d=val[['cvegeo','estado','anio','produccion_t','produccion_lag2']].copy()
            d['algoritmo']=name;d['prediccion_t']=pred;d['fase']=phase
            records.append(d)
    detail=pd.DataFrame(folds)
    summary={'algoritmo':name,'fase':phase,**metrics(truth,estimated),
             'entrenamiento_total_s':detail.entrenamiento_total_s.sum(),
             'entrenamiento_por_ventana_s':detail.entrenamiento_total_s.mean(),
             'prediccion_total_s':detail.prediccion_s.sum(),
             'columnas_efectivas_max':int(detail.columnas_efectivas.max()),
             'convergencia_todas':bool(detail.convergencia.all()),
             'reintentos':int(detail.reintento_presupuesto.sum()),
             'negativas_limitadas':int(detail.negativas_limitadas.sum())}
    return summary,detail,pd.concat(records,ignore_index=True) if records else None

def initial_comparison(frame,out=None,progress=False):
    summaries=[];folds=[];predictions=[]
    for name in ALGORITHMS+['Ridge A3','Persistencia t-2']:
        s,d,p=cv_evaluate(frame,name,phase='ranking',keep_predictions=True)
        summaries.append(s);folds.append(d);predictions.append(p)
        if out:
            pd.DataFrame(summaries).to_csv(Path(out)/'ranking_en_progreso.csv',index=False)
        if progress:print(name,'MAE',round(s['MAE_t'],3),'s',round(s['entrenamiento_total_s'],3),'convergente',s['convergencia_todas'],flush=True)
    summary=pd.DataFrame(summaries).sort_values('MAE_t').reset_index(drop=True)
    eligible=summary.loc[summary.algoritmo.isin(ALGORITHMS)&summary.convergencia_todas]
    assert len(eligible)>=6,'Se requieren al menos seis algoritmos ajustados y convergentes.'
    finalists=eligible.head(2).algoritmo.tolist()
    return summary,pd.concat(folds,ignore_index=True),pd.concat(predictions,ignore_index=True),finalists

def coarse_pool(name):
    axes={'features':list(FEATURE_SETS)}
    if name=='Cuantil':axes.update(alpha=[0.0,.0001,.001,.01,.1,1.0])
    elif name=='Huber':axes.update(epsilon=[1.1,1.2,1.35,1.5,1.8,2.0],alpha=[1e-6,1e-4,.01,1.0,100.0])
    elif name=='ElasticNet':axes.update(alpha=[1e-5,1e-4,.001,.01,.1],l1_ratio=[.05,.2,.5,.8,.95,1.0])
    elif name=='CART':axes.update(max_depth=[3,6,10,16,None],min_samples_leaf=[1,5,10,25,50],ccp_alpha=[0.0,.0001,.001,.01])
    elif name=='KNN':axes.update(n_neighbors=[3,5,9,17,33,65],weights=['uniform','distance'],p=[1,2])
    elif name=='SVR':axes.update(C=[.1,1.,10.,100.,1000.],epsilon=[.005,.02,.1,.2],gamma=['scale',.01,.1,1.0],kernel=['rbf','linear'])
    elif name=='MLP':axes.update(hidden_layer_sizes=[[16],[32],[64],[32,16],[64,32]],activation=['relu','tanh'],alpha=[1e-5,.001,.1],learning_rate_init=[.0003,.001,.003,.01])
    names=list(axes)
    values=[dict(zip(names,items)) for items in product(*(axes[n] for n in names))]
    if name=='SVR':
        # gamma no interviene con kernel lineal: se canoniza para no duplicar pruebas.
        for v in values:
            if v['kernel']=='linear':v['gamma']='scale'
    unique={canonical(v):v for v in values}
    return list(unique.values()),axes

def refine_one(name,best,feature_choices,rng):
    p=dict(best);p['features']=str(rng.choice(feature_choices))
    def lognear(x,low,high):return float(np.clip(10**(np.log10(max(x,low))+rng.uniform(-1,1)),low,high))
    if name=='Cuantil':
        p['alpha']=lognear(p['alpha'] if p['alpha']>0 else .0001,1e-8,1.0)
    elif name=='Huber':
        p['alpha']=lognear(p['alpha'],1e-9,1000.0);p['epsilon']=float(np.clip(p['epsilon']+rng.normal(0,.2),1.01,2.5))
    elif name=='ElasticNet':
        p['alpha']=lognear(p['alpha'],1e-8,1.0);p['l1_ratio']=float(np.clip(p['l1_ratio']+rng.normal(0,.15),.02,1.0))
    elif name=='CART':
        depth=p['max_depth']
        p['max_depth']=int(rng.choice([8,12,16,20])) if depth is None else int(np.clip(depth+int(rng.integers(-3,4)),2,30))
        p['min_samples_leaf']=int(np.clip(p['min_samples_leaf']+rng.integers(-max(2,p['min_samples_leaf']//2),max(3,p['min_samples_leaf']//2+1)),1,80))
        p['ccp_alpha']=lognear(max(p['ccp_alpha'],.0001),1e-7,.1)
    elif name=='KNN':
        p['n_neighbors']=int(np.clip(round(p['n_neighbors']+rng.normal(0,max(2,p['n_neighbors']/3))),1,101))
        p['weights']=str(rng.choice(['uniform','distance']));p['p']=int(rng.choice([1,2]))
    elif name=='SVR':
        p['C']=lognear(p['C'],1e-3,1e4);p['epsilon']=lognear(p['epsilon'],1e-4,.5)
        if p['kernel']=='rbf':p['gamma']=str('scale') if rng.random()<.3 else float(10**rng.uniform(-3,0))
    elif name=='MLP':
        p['alpha']=lognear(p['alpha'],1e-8,1.0);p['learning_rate_init']=lognear(p['learning_rate_init'],1e-5,.03)
        p['hidden_layer_sizes']=[int(np.clip(k+rng.choice([-8,0,8]),8,96)) for k in p['hidden_layer_sizes']]
        p['activation']=str(rng.choice(['relu','tanh']))
    return p

def tune_model(frame,name,out,seed=42,n_total=48,progress=False):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    journal=out/f'busqueda_{name}.jsonl'
    journal.write_text('',encoding='utf-8')
    pool,axes=coarse_pool(name);default=dict(DEFAULTS[name]);seen={canonical(default)}
    others=[p for p in pool if canonical(p) not in seen]
    rng=np.random.default_rng(seed)
    n_extra=min(31,len(others))
    configs=[default]+[others[i] for i in rng.choice(len(others),n_extra,replace=False)]
    seen=set();rows=[];fold_rows=[]
    def run(config,stage):
        key=canonical(config)
        if key in seen:return False
        seen.add(key)
        try:
            s,d,_=cv_evaluate(frame,name,config,phase='ajuste')
            s['estado_experimento']='completo' if s['convergencia_todas'] else 'sin_convergencia'
            s['error_numerico']=''
        except (ValueError,FloatingPointError,OverflowError,RuntimeError) as error:
            # Una configuración numéricamente inviable se documenta y no compite.
            s={'algoritmo':name,'fase':'ajuste','MAE_t':np.inf,'RMSE_t':np.nan,
               'WAPE_pct':np.nan,'convergencia_todas':False,'entrenamiento_total_s':np.nan,
               'estado_experimento':'error_numerico','error_numerico':str(error)}
            d=pd.DataFrame()
        row={**s,'experimento':len(rows)+1,'etapa':stage,'config_id':config_id(name,config),
             'configuracion':key,'features':config['features']}
        rows.append(row)
        if len(d):
            d['config_id']=row['config_id'];fold_rows.append(d)
        with journal.open('a',encoding='utf-8') as stream:stream.write(json.dumps(row,ensure_ascii=False)+'\n')
        pd.DataFrame(rows).to_csv(out/f'busqueda_{name}.csv',index=False)
        if progress and (len(rows)%4==0 or len(rows)==1):print(name,'experimento',len(rows),'MAE',round(s['MAE_t'],3),flush=True)
        return True
    for config in configs:run(config,'exploracion')
    coarse=pd.DataFrame(rows)
    eligible=coarse.loc[coarse.convergencia_todas]
    assert len(eligible)>0,f'Sin configuración convergente: {name}'
    best=json.loads(eligible.sort_values('MAE_t').iloc[0].configuracion)
    feature_choices=eligible.groupby('features').MAE_t.min().sort_values().index.tolist()[:2]
    trials=0
    while len(rows)<n_total:
        trials+=1
        assert trials<10000
        config=refine_one(name,best,feature_choices,rng)
        run(config,'refinamiento')
    results=pd.DataFrame(rows)
    valid=results.loc[results.convergencia_todas]
    assert len(valid)>=max(12,int(.75*n_total)),f'Exploración válida insuficiente: {name}'
    chosen=valid.sort_values(['MAE_t','config_id']).iloc[0]
    best_config=json.loads(chosen.configuracion)
    # Menor MAE manda; el identificador hace determinista un empate exacto.
    detail=pd.concat(fold_rows,ignore_index=True)
    results.to_csv(out/f'busqueda_{name}.csv',index=False)
    detail.to_csv(out/f'busqueda_{name}_por_ventana.csv',index=False)
    return results,detail,best_config,axes

def choose_final(confirmation,configs):
    tuned=confirmation.loc[confirmation.version.eq('ajustado')].copy()
    best=float(tuned.MAE_t.min())
    acceptable=tuned.loc[tuned.MAE_t<=1.01*best].copy()
    acceptable['prioridad_interpretabilidad']=acceptable.algoritmo.map(SIMPLICITY)
    acceptable['entradas_originales']=acceptable.algoritmo.map(lambda n:len(FEATURE_SETS[configs[n]['features']]))
    acceptable=acceptable.sort_values(['prioridad_interpretabilidad','entradas_originales','MAE_t','algoritmo'])
    return str(acceptable.iloc[0].algoritmo),acceptable

"""Ingeniería reproducible de oferta municipal de aguacate. Equipo 4, Avance 2.

El año objetivo t utiliza exclusivamente atributos medidos en t-2 o antes.
El ajuste estadístico se limita al periodo de entrenamiento. No se modelan
rutas, costos ni emisiones que no estén observados en los datos de origen.
"""
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd
from sklearn.preprocessing import PowerTransformer, StandardScaler, OneHotEncoder
from sklearn.feature_selection import VarianceThreshold
from sklearn.decomposition import PCA

RAW_SHA256 = 'f195190c043409188741ea4a6a2bbb44343aaeaa1f2e02dc17b6bd5f394f9dd3'
KEY = ['AÑO','CVE_ENT','CVE_MUN','CVE_DDR','CVE_CADER','CVE_CICLO',
       'CVE_MODALIDAD','CVE_UNIDAD','CVE_CULTIVO']
ADDITIVE = {'SUPERFICIE_SEMBRADA':'sembrada_ha',
            'SUPERFICIE_COSECHADA':'cosechada_ha',
            'SUPERFICIE_SINIESTRADA':'siniestrada_ha',
            'VOLUMEN_PRODUCCION':'produccion_t',
            'VALOR_PRODUCCION':'valor_mxn'}
NUMERIC = ['produccion_lag2','produccion_lag3','produccion_lag4',
           'cosechada_lag2','sembrada_lag2','valor_lag2','rendimiento_lag2',
           'precio_lag2','valor_por_ha_lag2','media_produccion_3','sd_produccion_3',
           'cv_produccion_3','min_produccion_3','max_produccion_3',
           'cambio_log_produccion','cambio_log_cosechada','fraccion_cosechada_lag2',
           'fraccion_siniestrada_lag2','fraccion_riego_lag2',
           'participacion_estatal_lag2','n_observaciones_3','indice_anio']
BOUNDED = {'fraccion_cosechada_lag2','fraccion_siniestrada_lag2',
           'fraccion_riego_lag2','participacion_estatal_lag2',
           'n_observaciones_3','indice_anio'}
CATEGORICAL = ['estado_lag2','perfil_riego_lag2']

def read_raw(path, verify=True):
    path = Path(path)
    if verify:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == RAW_SHA256, 'Fuente distinta: revisar procedencia.'
    return pd.read_csv(path)

def safe_div(num, den):
    return num.div(den.where(den > 0))

def prepare_panel(raw):
    """Conserva conjuntos excluidos y agrega únicamente registros compatibles."""
    historical = raw.loc[raw['AÑO'] <= 2002].copy()
    quarantine = raw.loc[raw['AÑO'] == 2024].copy()
    eligible = raw.loc[(raw['AÑO'] >= 2003) & (raw['AÑO'] != 2024)].copy()
    assert not eligible.duplicated(KEY).any(), 'Claves administrativas ambiguas.'
    assert not (eligible['CVE_MUN'] == 999).any()
    assert eligible[list(ADDITIVE)].notna().all().all()
    assert eligible[list(ADDITIVE)].ge(0).all().all()
    eligible['cvegeo'] = eligible.CVE_ENT.astype(str).str.zfill(2) + eligible.CVE_MUN.astype(str).str.zfill(3)
    eligible['riego_ha'] = eligible.SUPERFICIE_COSECHADA.where(eligible.CVE_MODALIDAD.eq(1), 0)
    agg = {col:'sum' for col in ADDITIVE}
    agg.update({'riego_ha':'sum','ENTIDAD':'first','MUNICIPIO':'first','CVE_ENT':'first'})
    panel = eligible.groupby(['cvegeo','AÑO'], as_index=False).agg(agg).rename(columns=ADDITIVE).rename(columns={'AÑO':'anio'})
    panel['rendimiento_t_ha'] = safe_div(panel.produccion_t, panel.cosechada_ha)
    panel['precio_mxn_t'] = safe_div(panel.valor_mxn, panel.produccion_t)
    panel['valor_mxn_ha'] = safe_div(panel.valor_mxn, panel.cosechada_ha)
    panel['fraccion_cosechada'] = safe_div(panel.cosechada_ha, panel.sembrada_ha)
    panel['fraccion_siniestrada'] = safe_div(panel.siniestrada_ha, panel.sembrada_ha)
    panel['fraccion_riego'] = safe_div(panel.riego_ha, panel.cosechada_ha)
    totals = panel.groupby(['CVE_ENT','anio']).produccion_t.transform('sum')
    panel['participacion_estatal'] = safe_div(panel.produccion_t, totals)
    panel['perfil_riego'] = np.select([panel.cosechada_ha.eq(0),panel.fraccion_riego.eq(0),panel.fraccion_riego.eq(1)],
                                    ['Sin cosecha','Temporal','Riego'], default='Mixto')
    panel['estado'] = panel.CVE_ENT.astype(str).str.zfill(2)
    assert not panel.duplicated(['cvegeo','anio']).any()
    np.testing.assert_allclose(panel.produccion_t.sum(), eligible.VOLUMEN_PRODUCCION.sum())
    return panel.sort_values(['cvegeo','anio']).reset_index(drop=True), historical, quarantine

def build_features(panel):
    """Calendario completo por municipio; ausencia de registro nunca equivale a cero."""
    index = pd.MultiIndex.from_product([sorted(panel.cvegeo.unique()), range(2003,2026)], names=['cvegeo','anio'])
    grid = panel.set_index(['cvegeo','anio']).reindex(index)
    g = grid.groupby(level='cvegeo', sort=False)
    f = pd.DataFrame(index=index)
    f['produccion_t'] = grid.produccion_t
    f['observado_objetivo'] = grid.produccion_t.notna()
    for lag in [2,3,4]:
        f[f'produccion_lag{lag}'] = g.produccion_t.shift(lag)
    sources = {'cosechada_ha':'cosechada','sembrada_ha':'sembrada','valor_mxn':'valor',
               'rendimiento_t_ha':'rendimiento','precio_mxn_t':'precio','valor_mxn_ha':'valor_por_ha',
               'fraccion_cosechada':'fraccion_cosechada','fraccion_siniestrada':'fraccion_siniestrada',
               'fraccion_riego':'fraccion_riego','participacion_estatal':'participacion_estatal',
               'estado':'estado','perfil_riego':'perfil_riego'}
    for source, dest in sources.items():
        f[dest+'_lag2'] = g[source].shift(2)
    hist = f[[f'produccion_lag{i}' for i in [2,3,4]]]
    f['n_observaciones_3'] = hist.notna().sum(axis=1)
    enough = f.n_observaciones_3.ge(2)
    f['media_produccion_3'] = hist.mean(axis=1).where(enough)
    f['sd_produccion_3'] = hist.std(axis=1, ddof=1).where(enough)
    f['min_produccion_3'] = hist.min(axis=1).where(enough)
    f['max_produccion_3'] = hist.max(axis=1).where(enough)
    f['cv_produccion_3'] = safe_div(f.sd_produccion_3, f.media_produccion_3)
    f['cambio_log_produccion'] = np.log1p(f.produccion_lag2) - np.log1p(f.produccion_lag3)
    f['cambio_log_cosechada'] = np.log1p(f.cosechada_lag2) - np.log1p(g.cosechada_ha.shift(3))
    f['indice_anio'] = f.index.get_level_values('anio') - 2003
    f['sin_cosecha_lag2'] = f.cosechada_lag2.eq(0).astype(int)
    f = f.reset_index()
    f['anio_ultima_medicion'] = f.anio - 2
    f['con_historia_minima'] = f.produccion_lag2.notna()
    f['particion'] = np.select([f.anio.between(2007,2015), f.anio.between(2018,2020), f.anio.eq(2023), f.anio.eq(2025)],
                              ['train','validacion','reserva_2023','aplicacion_2025'], default='fuera_de_particion')
    f['elegible'] = f.observado_objetivo & f.con_historia_minima & f.particion.ne('fuera_de_particion')
    return f

def abs_skew(x):
    s = pd.Series(x)
    return float(abs(s.skew())) if s.nunique() > 1 else 0.0

class FeaturePreparation:
    """Transformaciones ajustadas en train; dos representaciones: interpretable y PCA."""
    def __init__(self, corr_threshold=0.95, pca_variance=0.95, min_frequency=30):
        self.corr_threshold = corr_threshold
        self.pca_variance = pca_variance
        self.min_frequency = min_frequency

    def _categories(self, data):
        out = data[CATEGORICAL].fillna('Sin dato').astype(str).copy()
        out['escala_produccion'] = pd.cut(data.produccion_lag2, self.bin_edges_, labels=self.bin_labels_,
                                        include_lowest=True).astype('object').fillna('Sin dato')
        return out

    def _shape_transform(self, data):
        x = data[NUMERIC].replace([np.inf,-np.inf],np.nan).fillna(self.medians_).astype(float)
        for c, method in self.methods_.items():
            if method == 'log1p':
                if x[c].min() < 0:
                    raise ValueError(f'Fuera del dominio log1p: {c}')
                x[c] = np.log1p(x[c])
            elif method == 'yeo-johnson':
                x[c] = self.powers_[c].transform(x[[c]]).ravel()
        return x

    def _extra(self, data):
        missing = data[NUMERIC].isna().astype(float).add_prefix('falta_')
        missing['sin_cosecha_lag2'] = data.sin_cosecha_lag2.astype(float)
        encoded = self.encoder_.transform(self._categories(data))
        return pd.DataFrame(np.c_[missing.to_numpy(),encoded],index=data.index,columns=self.extra_names_)

    def full(self, data):
        z = pd.DataFrame(self.scaler_.transform(self._shape_transform(data)), columns=NUMERIC, index=data.index)
        return pd.concat([z,self._extra(data)],axis=1)

    def selected(self, data):
        return self.full(data)[self.selected_names_]

    def pca(self, data):
        s = self.selected(data)
        pc = self.pca_.transform(s[self.selected_numeric_])
        names = [f'PC{i+1:02d}' for i in range(pc.shape[1])]
        return pd.concat([pd.DataFrame(pc,index=data.index,columns=names),s[self.selected_other_]],axis=1)

    def fit(self, train):
        assert train.particion.eq('train').all(), 'Solo se admite entrenamiento.'
        self.fit_years_ = sorted(train.anio.unique().tolist())
        self.fit_n_ = len(train)
        self.medians_ = train[NUMERIC].median()
        assert self.medians_.notna().all(), 'Columna totalmente ausente en entrenamiento.'
        x = train[NUMERIC].fillna(self.medians_).astype(float)
        self.methods_, self.powers_ = {}, {}
        rows = []
        for c in NUMERIC:
            original = abs_skew(x[c])
            logskew = abs_skew(np.log1p(x[c])) if x[c].min() >= 0 else np.nan
            yjskew, power = np.nan, None
            # Constantes y proporciones se preservan; no se fuerza normalidad.
            if c not in BOUNDED and x[c].nunique() > 2:
                power = PowerTransformer(method='yeo-johnson',standardize=False)
                transformed = power.fit_transform(x[[c]]).ravel()
                yjskew = abs_skew(transformed)
            method, best = 'identidad', original
            if c not in BOUNDED and original > 1:
                if np.isfinite(logskew) and logskew < 0.8*original:
                    method, best = 'log1p', logskew
                if np.isfinite(yjskew) and yjskew < 0.8*original and yjskew < best-0.2:
                    method, best = 'yeo-johnson', yjskew
            self.methods_[c] = method
            if method == 'yeo-johnson':
                self.powers_[c] = power
            rows.append({'variable':c,'asimetria_abs_original':original,'asimetria_abs_log1p':logskew,
                         'asimetria_abs_yeojohnson':yjskew,'metodo':method,'asimetria_abs_elegida':best,
                         'curtosis_exceso_original':x[c].kurt(),
                         'lambda_yj_elegida':float(power.lambdas_[0]) if method=='yeo-johnson' else np.nan})
        self.transform_report_ = pd.DataFrame(rows)
        shaped = self._shape_transform(train)
        self.scaler_ = StandardScaler().fit(shaped)
        self.scaling_report_ = pd.DataFrame({'variable':NUMERIC,'media_entrenamiento':self.scaler_.mean_,
                                             'escala_entrenamiento':self.scaler_.scale_,
                                             'mediana_imputacion':self.medians_.to_numpy()})
        internal = np.unique(train.produccion_lag2.quantile([.25,.50,.75]).to_numpy())
        self.bin_edges_ = np.r_[-np.inf,internal,np.inf]
        self.bin_labels_ = [f'Q{i+1}' for i in range(len(self.bin_edges_)-1)]
        self.encoder_ = OneHotEncoder(handle_unknown='infrequent_if_exist',min_frequency=self.min_frequency,
                                      sparse_output=False,dtype=float).fit(self._categories(train))
        self.extra_names_ = ['falta_'+c for c in NUMERIC]+['sin_cosecha_lag2']+self.encoder_.get_feature_names_out().tolist()
        full = self.full(train)
        self.variance_ = VarianceThreshold(threshold=0).fit(full)
        variable = full.columns[self.variance_.get_support()].tolist()
        self.constant_names_ = [c for c in full if c not in variable]
        numeric_active = [c for c in NUMERIC if c in variable]
        self.corr_ = full[numeric_active].corr(method='spearman')
        kept, removed = [], []
        # Orden público definido por el dominio: nivel reciente, áreas, productividad,
        # precios, luego memoria/resúmenes. No se consulta y ni validación.
        for c in numeric_active:
            conflicts = [(k,float(self.corr_.loc[c,k])) for k in kept if abs(self.corr_.loc[c,k]) > self.corr_threshold]
            if conflicts:
                k,rho = max(conflicts,key=lambda z:abs(z[1]))
                removed.append({'variable_eliminada':c,'variable_conservada':k,'rho_spearman':rho,
                                'criterio':f'|rho| > {self.corr_threshold}; prioridad de dominio'})
            else:
                kept.append(c)
        self.selected_numeric_ = kept
        # Indicadores idénticos no aportan información adicional en entrenamiento.
        # Priorizar el significado de sin cosecha sobre indicadores técnicos.
        other = [c for c in variable if c not in NUMERIC]
        other = sorted(other,key=lambda c: (c != 'sin_cosecha_lag2',variable.index(c)))
        unique, duplicates = [], []
        for c in other:
            same = next((k for k in unique if np.array_equal(full[c].to_numpy(),full[k].to_numpy())),None)
            if same is None:
                unique.append(c)
            else:
                duplicates.append({'variable_eliminada':c,'variable_conservada':same,
                                   'criterio':'Indicadores idénticos en entrenamiento'})
        self.duplicate_report_ = pd.DataFrame(duplicates)
        self.selected_other_ = unique
        self.selected_names_ = self.selected_numeric_+self.selected_other_
        self.correlation_report_ = pd.DataFrame(removed)
        self.pca_ = PCA(n_components=self.pca_variance,svd_solver='full').fit(full[self.selected_numeric_])
        self.pca_all_ = PCA(svd_solver='full').fit(full[self.selected_numeric_])
        self.pca_report_ = pd.DataFrame({'componente':np.arange(1,len(self.pca_all_.explained_variance_ratio_)+1),
                                        'varianza_explicada':self.pca_all_.explained_variance_ratio_,
                                        'varianza_acumulada':np.cumsum(self.pca_all_.explained_variance_ratio_)})
        return self

def feature_dictionary():
    rows=[]
    def add(name, formula, unit, reason, latest='t-2'):
        rows.append(dict(variable=name,construccion=formula,unidad=unit,ultima_medicion=latest,justificacion=reason))
    for lag in [2,3,4]:
        add(f'produccion_lag{lag}',f'Producción municipal observada en t-{lag}','t',
            'Persistencia e historia de oferta; no sustituye una ausencia por cero.',f't-{lag}')
    for base,unit,meaning in [('cosechada','ha','Capacidad efectivamente cosechada'),('sembrada','ha','Base territorial plantada'),
                              ('valor','MXN nominales','Escala económica histórica'),('rendimiento','t/ha','Productividad agronómica'),
                              ('precio','MXN nominales/t','Señal de valor unitario local'),('valor_por_ha','MXN nominales/ha','Intensidad económica')]:
        add(base+'_lag2',base+' del panel municipal en t-2',unit,meaning+'; no equivale a causalidad.')
    for prefix,formula,unit in [('media','media','t'),('sd','desviación estándar muestral ddof=1','t'),('min','mínimo','t'),('max','máximo','t')]:
        add(prefix+'_produccion_3',formula+' sobre t-2,t-3,t-4; mínimo 2 observaciones',unit,'Resume nivel, variación y extremos del historial.')
    add('cv_produccion_3','sd_produccion_3 / media_produccion_3 si media>0','adimensional','Variabilidad relativa; indefinida si media=0.')
    for var in ['produccion','cosechada']:
        add('cambio_log_'+var,f'log1p({var}[t-2])-log1p({var}[t-3])','adimensional','Cambio suavizado que admite ceros; no es tasa porcentual exacta.')
    for name,formula,reason in [('fraccion_cosechada','cosechada/sembrada','Aprovechamiento de superficie'),
                                ('fraccion_siniestrada','siniestrada/sembrada','Antecedente de afectación'),
                                ('fraccion_riego','ha cosechadas en riego/ha cosechadas totales','Dependencia del riego'),
                                ('participacion_estatal','producción municipal/producción estatal del mismo año','Concentración de oferta en el estado')]:
        add(name+'_lag2',formula+' en t-2, denominador>0','proporción',reason+'; no es distancia, costo ni emisión.')
    add('n_observaciones_3','Conteo no faltante en t-2,t-3,t-4','conteo','Calidad/cobertura del historial.')
    add('indice_anio','Año objetivo - 2003','años','Tendencia determinista conocida en el origen.','calendario conocido')
    add('sin_cosecha_lag2','1 si cosechada[t-2]=0, 0 de otro modo','binaria','Conserva el estado sin cosecha.')
    add('estado_lag2','CVE_ENT de la observación t-2; one-hot','categoría','Contexto territorial; clave no implica orden.')
    add('perfil_riego_lag2','Sin cosecha, Temporal (0), Riego (1), Mixto (0<fracción<1); one-hot','categoría','Composición tecnológica observada, no clima medido.')
    add('escala_produccion','Cuartiles de produccion_lag2 aprendidos solo en train; one-hot','categoría','Relación por tramos sin imponer distancias iguales entre categorías.')
    add('falta_*','1 si el atributo numérico está ausente antes de imputar','binaria','Distingue valores observados de la mediana usada para el algoritmo.')
    return pd.DataFrame(rows)

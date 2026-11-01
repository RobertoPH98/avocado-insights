"""Ensambles y evaluación temporal del Avance 5; sin particiones aleatorias de años."""
from pathlib import Path
from itertools import product
import json,time,hashlib,warnings
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.linear_model import Ridge,HuberRegressor
from sklearn.ensemble import BaggingRegressor,RandomForestRegressor,ExtraTreesRegressor,HistGradientBoostingRegressor
from sklearn.exceptions import ConvergenceWarning
from modelos_avance4 import IndividualModel,DEFAULTS,ALGORITHMS,FEATURE_SETS,canonical,config_id,load_frame
from baseline_avance3 import make_model as make_ridge,metrics,state_bootstrap

ENSEMBLES=['Bagging Huber','Random Forest','Extra Trees','HistGradientBoosting','Voting H-Q','Stacking temporal','Blending temporal']
HOMOGENEOUS=ENSEMBLES[:4]
HETEROGENEOUS=ENSEMBLES[4:]
INITIAL={
 'Bagging Huber':{'n_estimators':16,'max_samples':.8,'max_features':1.0,'features':'completo','target':'nivel'},
 'Random Forest':{'n_estimators':96,'max_depth':6,'min_samples_leaf':10,'max_features':1.0,'features':'completo','target':'residuo'},
 'Extra Trees':{'n_estimators':96,'max_depth':8,'min_samples_leaf':5,'max_features':1.0,'features':'completo','target':'residuo'},
 'HistGradientBoosting':{'max_iter':100,'max_leaf_nodes':7,'learning_rate':.05,'min_samples_leaf':15,'l2_regularization':1.0,'features':'completo','target':'residuo'},
 'Voting H-Q':{'peso_Huber':.5},
 'Stacking temporal':{'inner_years':3,'meta':'ridge','alpha':1.0},
 'Blending temporal':{'blend_years':2,'meta':'ridge','alpha':1.0}}
COMPLEXITY={'Persistencia t-2':0,'Ridge A3':1,'ElasticNet':2,'Huber':2,'Cuantil':2,
 'CART':3,'Voting H-Q':4,'Blending temporal':5,'Stacking temporal':6,
 'Bagging Huber':7,'KNN':8,'Random Forest':9,'Extra Trees':9,'HistGradientBoosting':10,'SVR':11,'MLP':12}
# Caché únicamente dentro de una ejecución, identificada por todos los valores del entrenamiento.
_CACHE={}

def fingerprint(frame):
    cols=list(FEATURE_SETS['completo'])+['anio','cvegeo','produccion_t']
    return hashlib.sha256(pd.util.hash_pandas_object(frame[cols],index=True).values.tobytes()).hexdigest()

def base_configs(root):
    obj=json.loads((Path(root)/'documentacion/avance4/configuraciones_ajustadas.json').read_text())
    assert set(obj)=={'Huber','Cuantil'}
    return obj

def fit_base(train,name,configs,cache=False):
    key=('base',fingerprint(train),name,canonical(configs[name])) if cache else None
    if key is not None and key in _CACHE:return _CACHE[key]
    model=IndividualModel(name,configs[name]).fit(train)
    assert model.converged_,f'Base sin convergencia: {name}'
    if key is not None:_CACHE[key]=model
    return model

class Preparation:
    def __init__(self,features='completo'):self.columns=list(FEATURE_SETS[features])
    def fit(self,frame):
        x=frame[self.columns].to_numpy(float)
        self.imputer_=SimpleImputer(strategy='median',keep_empty_features=True).fit(x)
        full=np.c_[self.imputer_.transform(x),np.isnan(x).astype(float)]
        self.filter_=VarianceThreshold(0).fit(full)
        self.scaler_=StandardScaler().fit(self.filter_.transform(full))
        self.names_=np.asarray(self.columns+['falta_'+c for c in self.columns])[self.filter_.get_support()].tolist()
        return self
    def transform(self,frame):
        x=frame[self.columns].to_numpy(float)
        full=np.c_[self.imputer_.transform(x),np.isnan(x).astype(float)]
        return self.scaler_.transform(self.filter_.transform(full))

class TreeEnsemble:
    def __init__(self,name,config,configs):self.name=name;self.config=dict(config);self.configs=configs
    def fit(self,frame,cache=False):
        start=time.perf_counter();self.train_end_=int(frame.anio.max());self.n_train_=len(frame)
        self.prep_=Preparation(self.config['features']).fit(frame)
        x=self.prep_.transform(frame)
        y=frame.produccion_t.to_numpy(float)
        if self.config['target']=='residuo':y=y-frame.produccion_lag2.to_numpy(float)
        self.y_scaler_=StandardScaler().fit(y.reshape(-1,1));z=self.y_scaler_.transform(y.reshape(-1,1)).ravel()
        pars={k:v for k,v in self.config.items() if k not in {'features','target'}}
        if self.name=='Bagging Huber':
            h=self.configs['Huber']
            estimator=HuberRegressor(epsilon=h['epsilon'],alpha=h['alpha'],max_iter=18000,tol=1e-6)
            self.estimator_=BaggingRegressor(estimator=estimator,**pars,bootstrap=True,random_state=42,n_jobs=1)
        elif self.name=='Random Forest':self.estimator_=RandomForestRegressor(**pars,criterion='squared_error',bootstrap=True,random_state=42,n_jobs=1)
        elif self.name=='Extra Trees':self.estimator_=ExtraTreesRegressor(**pars,criterion='squared_error',bootstrap=False,random_state=42,n_jobs=1)
        elif self.name=='HistGradientBoosting':self.estimator_=HistGradientBoostingRegressor(**pars,loss='absolute_error',early_stopping=False,random_state=42)
        else:raise ValueError(self.name)
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter('always');self.estimator_.fit(x,z)
        self.messages_=[str(w.message) for w in captured]
        self.converged_=not any(issubclass(w.category,ConvergenceWarning) for w in captured)
        self.fit_s_=time.perf_counter()-start
        self.audit_=[];self.columns=self.prep_.columns
        return self
    def predict_raw(self,frame):
        y=self.y_scaler_.inverse_transform(self.estimator_.predict(self.prep_.transform(frame)).reshape(-1,1)).ravel()
        if self.config['target']=='residuo':y=y+frame.produccion_lag2.to_numpy(float)
        return y
    def predict(self,frame):return np.maximum(0,self.predict_raw(frame))

class MetaRegressor:
    def __init__(self,kind,alpha):self.kind=kind;self.alpha=alpha
    def fit(self,x,y):
        self.x_scale_=StandardScaler().fit(x);self.y_scale_=StandardScaler().fit(np.asarray(y).reshape(-1,1))
        z=self.x_scale_.transform(x);target=self.y_scale_.transform(np.asarray(y).reshape(-1,1)).ravel()
        self.estimator_=(Ridge(alpha=self.alpha,positive=True,solver='lbfgs',max_iter=20000,tol=1e-7)
            if self.kind=='ridge' else HuberRegressor(alpha=self.alpha,epsilon=1.35,max_iter=18000,tol=1e-6))
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always');self.estimator_.fit(z,target)
        self.messages_=[str(w.message) for w in ws]
        self.converged_=not any(issubclass(w.category,ConvergenceWarning) for w in ws)
        return self
    def predict(self,x):return self.y_scale_.inverse_transform(self.estimator_.predict(self.x_scale_.transform(x)).reshape(-1,1)).ravel()
    def coefficients(self):
        coef=self.estimator_.coef_*self.y_scale_.scale_[0]/self.x_scale_.scale_
        intercept=float(self.y_scale_.mean_[0]+self.y_scale_.scale_[0]*self.estimator_.intercept_-np.dot(coef,self.x_scale_.mean_))
        return coef.tolist(),intercept

def temporal_oof(train,configs,n_years,cache=False):
    key=('oof',fingerprint(train),n_years,canonical(configs)) if cache else None
    if key is not None and key in _CACHE:return _CACHE[key]
    last=int(train.anio.max());years=list(range(max(2010,last-n_years+1),last+1))
    xs=[];ys=[];records=[];keys=[]
    for year in years:
        inner=train.loc[train.anio.le(year-3)];val=train.loc[train.anio.eq(year)]
        assert len(inner)>100 and len(val)>0
        cols=[]
        for name in ['Huber','Cuantil']:
            model=fit_base(inner,name,configs,cache)
            cols.append(model.predict(val))
        xs.append(np.column_stack(cols));ys.append(val.produccion_t.to_numpy())
        keys.append(val[['cvegeo','anio']])
        records.append({'tipo':'OOF','anio_meta':year,'max_etiqueta_base':int(inner.anio.max()),'n_base':len(inner),'n_meta':len(val)})
    result=(np.vstack(xs),np.concatenate(ys),records,pd.concat(keys,ignore_index=True))
    if key is not None:_CACHE[key]=result
    return result

class Heterogeneous:
    def __init__(self,name,config,configs):self.name=name;self.config=dict(config);self.configs=configs
    def fit(self,train,cache=False):
        start=time.perf_counter();self.train_end_=int(train.anio.max());self.n_train_=len(train)
        self.messages_=[];self.audit_=[];self.meta_=None
        if self.name=='Blending temporal':
            last=int(train.anio.max());first=last-self.config['blend_years']+1
            early=train.loc[train.anio.le(first-3)]
            hold=train.loc[train.anio.between(first,last)]
            self.models_=[fit_base(early,name,self.configs,cache) for name in ['Huber','Cuantil']]
            x=np.column_stack([m.predict(hold) for m in self.models_])
            self.meta_=MetaRegressor(self.config['meta'],self.config['alpha']).fit(x,hold.produccion_t)
            self.audit_=[{'tipo':'Blending','anio_meta':int(y),'max_etiqueta_base':int(early.anio.max()),'n_base':len(early),'n_meta':int(hold.anio.eq(y).sum())} for y in sorted(hold.anio.unique())]
            self.meta_x_=x;self.meta_y_=hold.produccion_t.to_numpy()
            # Las bases de blending permanecen ajustadas con early, sin refit posterior.
        else:
            if self.name=='Stacking temporal':
                x,y,self.audit_,self.meta_keys_=temporal_oof(train,self.configs,self.config['inner_years'],cache)
                self.meta_=MetaRegressor(self.config['meta'],self.config['alpha']).fit(x,y)
                self.meta_x_=x;self.meta_y_=y
            self.models_=[fit_base(train,name,self.configs,cache) for name in ['Huber','Cuantil']]
        self.converged_=all(m.converged_ for m in self.models_) and (self.meta_ is None or self.meta_.converged_)
        if self.meta_:self.messages_=list(self.meta_.messages_)
        self.fit_s_=time.perf_counter()-start
        self.columns=list(FEATURE_SETS['completo'])
        return self
    def base_predictions(self,frame):return np.column_stack([m.predict(frame) for m in self.models_])
    def predict_raw(self,frame):
        x=self.base_predictions(frame)
        if self.meta_ is not None:return self.meta_.predict(x)
        w=self.config['peso_Huber'];return w*x[:,0]+(1-w)*x[:,1]
    def predict(self,frame):return np.maximum(0,self.predict_raw(frame))

class Individual:
    def __init__(self,name,configs):self.name=name;self.config=dict(configs.get(name,DEFAULTS.get(name,{})))
    def fit(self,train,cache=False):
        start=time.perf_counter();self.train_end_=int(train.anio.max());self.n_train_=len(train);self.audit_=[];self.messages_=[]
        if self.name=='Persistencia t-2':self.model_=None;self.converged_=True;self.columns=['produccion_lag2']
        elif self.name=='Ridge A3':self.model_=make_ridge('Ridge nivel').fit(train);self.converged_=True;self.columns=['produccion_lag2']
        else:
            self.model_=IndividualModel(self.name,self.config).fit(train);self.converged_=self.model_.converged_
            self.messages_=self.model_.fit_messages_;self.columns=self.model_.columns
        self.fit_s_=time.perf_counter()-start if self.model_ is not None else 0.0
        return self
    def predict_raw(self,frame):return frame.produccion_lag2.to_numpy() if self.model_ is None else self.model_.predict_raw(frame)
    def predict(self,frame):return np.maximum(0,self.predict_raw(frame))

def build(name,config,configs):
    if name in HOMOGENEOUS:return TreeEnsemble(name,config,configs)
    if name in HETEROGENEOUS:return Heterogeneous(name,config,configs)
    return Individual(name,configs)

def evaluate(frame,name,config,configs,years,cache=False):
    records=[];predictions=[];audits=[]
    for year in years:
        tr=frame.loc[frame.anio.between(2007,year-3)];va=frame.loc[frame.anio.eq(year)]
        model=build(name,config,configs).fit(tr,cache)
        start=time.perf_counter();raw=model.predict_raw(va);pred=np.maximum(0,raw);pred_s=time.perf_counter()-start
        assert np.isfinite(pred).all()
        records.append({'modelo':name,'anio':year,**metrics(va.produccion_t,pred),'entrenamiento_s':model.fit_s_,
                        'prediccion_s':pred_s,'fin_train':int(tr.anio.max()),'n_train':len(tr),'convergencia':model.converged_,
                        'negativas_limitadas':int((raw<0).sum()),'cache':cache,'advertencias':json.dumps(model.messages_,ensure_ascii=False)})
        d=va[['cvegeo','estado','anio','produccion_t','produccion_lag2']].copy();d['modelo']=name;d['prediccion_t']=pred;predictions.append(d)
        for a in model.audit_:audits.append({'modelo':name,'origen_externo':year,**a})
    p=pd.concat(predictions,ignore_index=True);r=pd.DataFrame(records)
    summary={'modelo':name,'estrategia':strategy(name),**metrics(p.produccion_t,p.prediccion_t),
             'entrenamiento_s':float(r.entrenamiento_s.sum()),'entrenamiento_promedio_s':float(r.entrenamiento_s.mean()),
             'prediccion_s':float(r.prediccion_s.sum()),'convergencia':bool(r.convergencia.all()),'cache':cache}
    return summary,r,p,pd.DataFrame(audits)

def strategy(name):return 'Homogéneo' if name in HOMOGENEOUS else 'Heterogéneo' if name in HETEROGENEOUS else 'Individual / referencia'

def parameter_space(name):
    if name=='Bagging Huber':return {'n_estimators':[8,16,32],'max_samples':[.6,.8,1.0],'max_features':[.75,1.0],'features':['completo','capacidad'],'target':['nivel']}
    if name in ['Random Forest','Extra Trees']:return {'n_estimators':[64,96,160],'max_depth':[4,8,12,None],'min_samples_leaf':[2,5,15,30],'max_features':[.6,1.0],'features':['completo','capacidad'],'target':['nivel','residuo']}
    if name=='HistGradientBoosting':return {'max_iter':[60,100,180],'max_leaf_nodes':[3,7,15],'learning_rate':[.025,.05,.1],'min_samples_leaf':[10,25,50],'l2_regularization':[0.,1.,10.],'features':['completo','capacidad'],'target':['nivel','residuo']}
    if name=='Voting H-Q':return {'peso_Huber':[float(round(x,2)) for x in np.linspace(.02,.98,25)]}
    if name=='Stacking temporal':return {'inner_years':[3,5],'meta':['ridge','huber'],'alpha':[.01,.1,1.,10.,100.,1000.]}
    if name=='Blending temporal':return {'blend_years':[1,2],'meta':['ridge','huber'],'alpha':[.01,.1,1.,10.,100.,1000.]}
    raise ValueError(name)

def choose_relevant(table):
    good=table.loc[table.modelo.isin(ENSEMBLES)&table.convergencia].sort_values(['MAE_t','modelo'])
    chosen=[good.loc[good.modelo.isin(HOMOGENEOUS)].iloc[0].modelo,good.loc[good.modelo.isin(HETEROGENEOUS)].iloc[0].modelo]
    chosen.append(good.loc[~good.modelo.isin(chosen)].iloc[0].modelo)
    return chosen

def tune(frame,name,configs,out,seed=42,budget=24):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    space=parameter_space(name);keys=list(space)
    pool=[dict(zip(keys,x)) for x in product(*(space[k] for k in keys))]
    rng=np.random.default_rng(seed);initial=dict(INITIAL[name]);chosen=[initial]
    for i in rng.permutation(len(pool)):
        p=pool[int(i)]
        if canonical(p) not in {canonical(c) for c in chosen}:chosen.append(p)
        if len(chosen)==budget:break
    assert len(chosen)==budget
    results=[];folds=[];audits=[]
    journal=out/(name.replace(' ','_')+'.jsonl');journal.write_text('')
    for i,config in enumerate(chosen,1):
        summary,detail,_,audit=evaluate(frame,name,config,configs,[2018,2019,2020],cache=True)
        row={**summary,'experimento':i,'config_id':config_id(name,config),'configuracion':canonical(config)}
        results.append(row);detail['experimento']=i;folds.append(detail)
        if not audit.empty:
            audit['experimento']=i;audits.append(audit)
        with journal.open('a') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
        pd.DataFrame(results).to_csv(out/(name.replace(' ','_')+'.csv'),index=False)
    res=pd.DataFrame(results);details=pd.concat(folds,ignore_index=True)
    details.to_csv(out/(name.replace(' ','_')+'_ventanas.csv'),index=False)
    if audits:pd.concat(audits,ignore_index=True).to_csv(out/(name.replace(' ','_')+'_auditoria_meta.csv'),index=False)
    good=res.loc[res.convergencia].sort_values(['MAE_t','config_id'])
    assert not good.empty
    best=json.loads(good.iloc[0].configuracion)
    return res,details,best

def select_final(table):
    candidates=table.loc[table.convergencia].copy()
    best=float(candidates.MAE_t.min())
    candidates['dentro_1pct']=candidates.MAE_t.le(best*1.01)
    candidates['complejidad']=candidates.modelo.map(COMPLEXITY)
    winner=candidates.loc[candidates.dentro_1pct].sort_values(['complejidad','MAE_t','modelo']).iloc[0].modelo
    return winner,candidates.sort_values('MAE_t')

def grouped_importance(model,frame,seed=42,repeats=8):
    groups={'Escala y capacidad':['produccion_lag2','cosechada_lag2','sembrada_lag2','log_produccion_lag2','log_cosechada_lag2','log_sembrada_lag2'],
       'Productividad':['rendimiento_lag2'],'Dinámica':['cambio_log_produccion','cv_produccion_3'],
       'Macroeconomía':['inflacion_usa_lag2','depreciacion_mxn_lag2','oferta_x_inflacion','oferta_x_depreciacion'],
       'Clima':['temperatura_estado_lag2','amplitud_mensual_lag2','cambio_temperatura_lag2','oferta_x_cambio_temperatura']}
    base=metrics(frame.produccion_t,model.predict(frame))['MAE_t'];rng=np.random.default_rng(seed);rows=[]
    for name,cols in groups.items():
        increases=[]
        for j in range(repeats):
            d=frame.copy()
            # Permutación conjunta del bloque dentro de cada año: conserva contexto temporal.
            for _,idx in d.groupby('anio').groups.items():
                ix=np.asarray(idx);per=rng.permutation(ix);d.loc[ix,cols]=frame.loc[per,cols].to_numpy()
            increases.append(metrics(d.produccion_t,model.predict(d))['MAE_t']-base)
        rows.append({'bloque':name,'aumento_MAE_t':float(np.mean(increases)),'sd_repeticiones_t':float(np.std(increases,ddof=1)),
                     'repeticiones':repeats,'metrica_base_t':base})
    return pd.DataFrame(rows).sort_values('aumento_MAE_t',ascending=False)

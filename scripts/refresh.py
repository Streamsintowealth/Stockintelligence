#!/usr/bin/env python3
"""Refresh SEC ticker directory, selected financial snapshots, and official economic data.
Run on GitHub Actions; SEC requests use a truthful contact user agent.
No fabricated values. Individual provider failures leave previous snapshots intact.
"""
import json, os, time, urllib.request, urllib.error, datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
UA=os.getenv('SEC_USER_AGENT','StreamsIntoWealthResearch research-contact@example.com')
HEAD={'User-Agent':UA,'Accept':'application/json'}
def get(url, headers=None, timeout=30):
    req=urllib.request.Request(url,headers=headers or HEAD)
    with urllib.request.urlopen(req,timeout=timeout) as r:return json.load(r)
def save(path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False))
def directory():
    url='https://www.sec.gov/files/company_tickers_exchange.json'
    j=get(url)
    rows=j.get('data',[])
    fields=j.get('fields',[])
    ix={k:i for i,k in enumerate(fields)}
    out=[]
    for row in rows:
        try:
            ticker=str(row[ix['ticker']]).strip()
            name=str(row[ix['name']]).strip()
            cik=int(row[ix['cik']])
            exchange=str(row[ix['exchange']]) if 'exchange' in ix else ''
            if ticker and name:out.append(dict(ticker=ticker,title=name,cik=cik,exchange=exchange))
        except (KeyError,ValueError,TypeError,IndexError):continue
    if len(out)<1000:raise RuntimeError('SEC directory unexpectedly small')
    save(DATA/'symbols.json',out)
    print('Saved SEC symbols:',len(out))
    return out
TAGS={
 'Revenue':['RevenueFromContractWithCustomerExcludingAssessedTax','Revenues','SalesRevenueNet','RevenueFromContractWithCustomerIncludingAssessedTax'],
 'NetIncome':['NetIncomeLoss'],
 'Assets':['Assets'],
 'Liabilities':['Liabilities'],
 'OperatingCashFlow':['NetCashProvidedByUsedInOperatingActivities'],
 'CapitalExpenditures':['PaymentsToAcquirePropertyPlantAndEquipment'],
 'EPS':['EarningsPerShareDiluted']
}
def pick(facts,tags):
    gaap=facts.get('facts',{}).get('us-gaap',{})
    for tag in tags:
        node=gaap.get(tag)
        if not node:continue
        unit='USD/shares' if tag=='EarningsPerShareDiluted' else 'USD'
        entries=node.get('units',{}).get(unit,[])
        # Avoid comparing annual values with quarterly values without a period label.
        rows=[x for x in entries if x.get('form') in ('10-K','10-Q') and x.get('filed') and x.get('end') and x.get('val') is not None]
        if not rows:continue
        rows.sort(key=lambda x:(x.get('filed',''),x.get('end',''),x.get('accn','')),reverse=True)
        x=rows[0]
        return {'value':x['val'],'end':x['end'],'start':x.get('start'),'filed':x['filed'],'form':x.get('form'),'tag':tag,'unit':unit}
    return None
def annual_history(facts,tags):
    gaap=facts.get('facts',{}).get('us-gaap',{})
    for tag in tags:
        node=gaap.get(tag)
        if not node:continue
        unit='USD/shares' if tag=='EarningsPerShareDiluted' else 'USD'
        items=node.get('units',{}).get(unit,[])
        annual=[]
        for x in items:
            if x.get('form') not in ('10-K','10-K/A') or x.get('val') is None or not x.get('end'):continue
            if x.get('start'):
                try:
                    days=(datetime.date.fromisoformat(x['end'])-datetime.date.fromisoformat(x['start'])).days
                    if not 330<=days<=390:continue
                except ValueError:continue
            elif tag not in ('Assets','Liabilities'):continue
            year=x.get('fy') or int(x['end'][:4])
            annual.append({'year':int(year),'value':x['val'],'end':x['end'],'filed':x.get('filed','')})
        if annual:
            # Prefer the latest filing of each fiscal year, without mixing annual and quarterly flows.
            chosen={}
            for x in sorted(annual,key=lambda x:(x['year'],x['filed'])):chosen[x['year']]=x
            return sorted(chosen.values(),key=lambda x:x['year'],reverse=True)[:8]
    return []
def profile(cik):
    try:
        sub=get('https://data.sec.gov/submissions/CIK'+str(cik).zfill(10)+'.json',timeout=30)
        return {'name':sub.get('name'),'industry':sub.get('sicDescription'),'sic':sub.get('sic'),'sector':None,
                'description':None,'website':sub.get('website'),'fiscalYearEnd':sub.get('fiscalYearEnd')}
    except Exception as e:
        print('Company metadata unavailable:',str(e)[:100]);return {}
def finance(rows):
    lookup={x['ticker']:x for x in rows}
    wanted=['NVDA','GOOGL','GOOG','MSFT','AAPL','AMZN','META','TSLA','AVGO','CRWD','NOW','AMD','JPM','GEV','GS','CAT','MU','WMT','COST','V','MA','DIS','NFLX','KO','PEP','UNH','XOM','PLTR']
    for ticker in wanted:
        x=lookup.get(ticker)
        if not x:continue
        try:
            cik=str(x['cik']).zfill(10)
            facts=get('https://data.sec.gov/api/xbrl/companyfacts/CIK'+cik+'.json',timeout=40)
            financials={key:pick(facts,tags) for key,tags in TAGS.items()}
            save(DATA/'stocks'/f'{ticker}.json',{'ticker':ticker,'cik':x['cik'],'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'financials':financials,'history':{key:annual_history(facts,tags) for key,tags in TAGS.items()},'profile':profile(x['cik']),'source':'SEC EDGAR XBRL and submissions'})
            print('Financials:',ticker)
        except Exception as e:print('Financials failed:',ticker,str(e)[:150])
        time.sleep(.25)
def economics():
    # Official BLS public API, no API key, most recent published observations.
    series={
        'CPI':('CUUR0000SA0','index','Consumer Price Index, all items, unadjusted'),
        'CoreCPI':('CUUR0000SA0L1E','index','CPI less food and energy, unadjusted'),
        'Unemployment':('LNS14000000','percent','Unemployment rate, seasonally adjusted'),
        'Payrolls':('CES0000000001','thousand jobs','Total nonfarm employment, seasonally adjusted'),
        'PPI':('WPUFD4','index','Final demand producer price index, unadjusted')
    }
    req={'seriesid':[s[0] for s in series.values()],'startyear':str(datetime.datetime.now().year-1),'endyear':str(datetime.datetime.now().year)}
    body=json.dumps(req).encode()
    request=urllib.request.Request('https://api.bls.gov/publicAPI/v2/timeseries/data/',data=body,headers={'Content-Type':'application/json','User-Agent':UA},method='POST')
    with urllib.request.urlopen(request,timeout=40) as resp:j=json.load(resp)
    if j.get('status')!='REQUEST_SUCCEEDED':raise RuntimeError(str(j.get('message')))
    reverse={v[0]:k for k,v in series.items()}
    result={'_updated':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    for series_obj in j.get('Results',{}).get('series',[]):
        key=reverse.get(series_obj.get('seriesID'))
        if not key:continue
        values=[d for d in series_obj.get('data',[]) if str(d.get('period','')).startswith('M') and d.get('period')!='M13']
        if not values:continue
        values.sort(key=lambda x:(x.get('year',''),x.get('period','')),reverse=True)
        d=values[0]
        current=float(d['value'])
        prev=float(values[1]['value']) if len(values)>1 else None
        if key in ('CPI','CoreCPI','PPI') and prev and prev!=0:
            display=f'{(current/prev-1)*100:+.2f}% MoM'
        elif key=='Payrolls' and prev is not None:
            display=f'{current-prev:+,.0f}K jobs MoM'
        elif key=='Unemployment':
            display=f'{current:.1f}%'
        else:
            display=d['value']+' '+series[key][1]
        result[key]={'value':display, 'date':f"{d['year']}-{d['period'][1:]}",'source':'BLS','series':series[key][2]}
    save(DATA/'economic.json',result)
    print('BLS series:',len(result)-1)
if __name__=='__main__':
    rows=None
    try:rows=directory()
    except Exception as e:print('SEC directory refresh failed:',e)
    if rows:
        finance(rows)
    try:economics()
    except Exception as e:print('BLS refresh failed:',e)

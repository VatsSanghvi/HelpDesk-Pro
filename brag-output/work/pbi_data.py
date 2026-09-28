import json, collections, datetime as dt
T=json.load(open('feed.json'))
for t in T:
    t['assigned_to']=t['assigned_to'] or 'Unassigned'
    t['priority_display']=t['priority'] or 'Not Yet Triaged'
def m(rows):
    n=len(rows); res=[r['resolution_time_hours'] for r in rows if r['resolution_time_hours'] is not None]
    return dict(total=n, open=sum(r['is_open'] for r in rows), resolved=sum(not r['is_open'] for r in rows),
      breaches=sum(bool(r['is_sla_breached']) for r in rows),
      compliance=(sum(not r['is_sla_breached'] for r in rows)/n if n else 0),
      avgres=(sum(res)/len(res) if res else None),
      highopen=sum(r['priority']=='High' and r['is_open'] for r in rows),
      unassigned=sum(r['assigned_to']=='Unassigned' for r in rows))
def group(key, rows=T):
    g=collections.defaultdict(list)
    for r in rows: g[key(r)].append(r)
    return g
day=lambda r: (dt.date.fromisoformat(r['created_at'][:10])-dt.timedelta(days=dt.date.fromisoformat(r['created_at'][:10]).weekday())).isoformat()
M=m(T)
def series(g,f,sort=None,desc=True):
    items=[(k,f(v)) for k,v in g.items()]
    items=[i for i in items if i[1] is not None]
    if sort=='key': items.sort()
    else: items.sort(key=lambda i:-i[1] if desc else i[1])
    return items
fmt=lambda d: 'w/c '+dt.date.fromisoformat(d).strftime('%d %b')
vol=series(group(day),len,'key'); vol=[(fmt(k),v) for k,v in vol]
brv=series(group(day),lambda v:sum(bool(r['is_sla_breached']) for r in v),'key'); brv=[(fmt(k),v) for k,v in brv]
openT=sorted([r for r in T if r['is_open']],key=lambda r:-r['age_hours'])
brT=sorted([r for r in T if r['is_sla_breached']],key=lambda r:-r['age_hours'])
def row(r,cols): return [r[c] for c in cols]
cat=group(lambda r:r['category']); sub=group(lambda r:(r['category'],r['subcategory'])); ag=group(lambda r:r['assigned_to'])
pages=[
 dict(name='Overview',title='Help Desk Overview',
  cards=[('Total Tickets',M['total'],'0'),('Open Tickets',M['open'],'0'),('High Priority Open',M['highopen'],'0'),('SLA Compliance %',M['compliance'],'%'),('Avg Resolution Time (Hrs)',M['avgres'],'h')],
  top=[dict(t='col',title='Ticket Volume Over Time',d=vol),
       dict(t='donut',title='Tickets by Priority',d=series(group(lambda r:r['priority_display']),len)),
       dict(t='bar',title='Tickets by Status',d=series(group(lambda r:r['status']),len))],
  bottom=[dict(t='bar',title='Avg Resolution Time by Category',d=[(k,round(v,1)) for k,v in series(cat,lambda v:m(v)['avgres'])],w=400),
          dict(t='table',title='Open Tickets',cols=['ticket_number','title','priority_display','status','assigned_to','age_hours'],
               heads=['ticket_number','title','priority','status','assigned_to','age_hours'],rows=[row(r,['ticket_number','title','priority_display','status','assigned_to','age_hours']) for r in openT],w=816)]),
 dict(name='SLA & Aging',title='SLA Performance & Ticket Aging',
  cards=[('SLA Compliance %',M['compliance'],'%'),('SLA Breaches',M['breaches'],'0'),('Open Tickets',M['open'],'0'),('High Priority Open',M['highopen'],'0'),('Avg Resolution Time (Hrs)',M['avgres'],'h')],
  top=[dict(t='col',title='SLA Breaches Over Time',d=brv),
       dict(t='bar',title='SLA Breaches by Category',d=[i for i in series(cat,lambda v:m(v)['breaches']) if i[1]]),
       dict(t='bar',title='SLA Breaches by Assignee',d=[i for i in series(ag,lambda v:m(v)['breaches']) if i[1]])],
  bottom=[dict(t='table',title='Breached Tickets',heads=['ticket_number','title','category','priority','status','assigned_to','due_by','age_hours'],
     rows=[[r['ticket_number'],r['title'],r['category'],r['priority_display'],r['status'],r['assigned_to'],dt.datetime.fromisoformat(r['due_by']).strftime('%d/%m/%Y %H:%M') if r['due_by'] else '',r['age_hours']] for r in brT],w=1232)]),
 dict(name='Category Deep-Dive',title='Category & Subcategory Deep-Dive',
  cards=[('Total Tickets',M['total'],'0'),('Open Tickets',M['open'],'0'),('Resolved Tickets',M['resolved'],'0'),('SLA Compliance %',M['compliance'],'%'),('Avg Resolution Time (Hrs)',M['avgres'],'h')],
  top=[dict(t='bar',title='Top 10 Subcategories by Volume',d=[(k[1],v) for k,v in series(sub,len)][:10],w=608),
       dict(t='bar',title='Avg Resolution Time by Category',d=[(k,round(v,1)) for k,v in series(cat,lambda v:m(v)['avgres'])],w=608)],
  bottom=[dict(t='table',title='Category Breakdown',heads=['category','subcategory','Total Tickets','Open Tickets','SLA Breaches','Avg Resolution Time (Hrs)'],
     rows=[[k[0],k[1],m(v)['total'],m(v)['open'],m(v)['breaches'],(f"{m(v)['avgres']:.1f} hrs" if m(v)['avgres'] is not None else '')] for k,v in sorted(sub.items())],w=1232)]),
 dict(name='Agent Workload',title='Agent Workload & Performance',
  cards=[('Total Tickets',M['total'],'0'),('Open Tickets',M['open'],'0'),('Unassigned Tickets',M['unassigned'],'0'),('SLA Compliance %',M['compliance'],'%'),('Avg Resolution Time (Hrs)',M['avgres'],'h')],
  top=[dict(t='col2',title='Open vs Resolved by Assignee',d=[(k,m(v)['open'],m(v)['resolved']) for k,v in sorted(ag.items(),key=lambda i:-len(i[1]))],legend=['Open Tickets','Resolved Tickets'],w=608),
       dict(t='bar',title='Avg Resolution Time by Assignee',d=[(k,round(v,1)) for k,v in series(ag,lambda v:m(v)['avgres'])],w=608)],
  bottom=[dict(t='table',title='Agent Scorecard',heads=['assigned_to','assigned_to_role','Total Tickets','Open Tickets','Resolved Tickets','SLA Breaches','SLA Compliance %','Avg Resolution Time (Hrs)'],
     rows=[[k,(v[0]['assigned_to_role'] or ''),m(v)['total'],m(v)['open'],m(v)['resolved'],m(v)['breaches'],f"{m(v)['compliance']*100:.1f}%",(f"{m(v)['avgres']:.1f} hrs" if m(v)['avgres'] is not None else '')] for k,v in sorted(ag.items())],w=1232)]),
]
json.dump(pages,open('pbi_data.json','w'),indent=1,default=str)
print(json.dumps(M)); print(pages[0]['top'][1]['d'], pages[0]['top'][2]['d'], pages[1]['top'][2]['d'])

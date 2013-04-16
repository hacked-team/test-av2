import os

from flask import Flask, render_template

from lib.web.models import db, app, init_db, Test, Result, Report
from lib.web.settings import DB_PATH

@app.route('/')
def index_view():
	""" Index page
	Shows list of reports
	"""
	title = "Reports"
	reports = Test.query.all()

	return render_template('index.html', title=title, reports=reports)

@app.route('/report/<t_id>/result/<r_id>')
def result_view(t_id, r_id):
	""" Test Result page
	Show results of scheduled test on spcific virtual machine
	"""
	test = Test.query.filter_by(id=t_id).first_or_404()
	result = Result.query.filter_by(test_id=t_id,id=r_id).first_or_404()

	if not result:
		result = None
	else:
		result.result = result.result.split(", ")

	return render_template("result.html", title=test.time, result=result)

@app.route('/results/<t_id>')
def results_view(t_id):
	test = Test.query.filter_by(id=t_id).first_or_404()
	results = Result.query.filter_by(test_id=t_id)
	return render_template("results.html", title=test.time, results=results)

@app.route('/report/<t_id>')
def report_view(t_id):
	""" Report page
	Show report page 
	"""
	test = Test.query.filter_by(id=t_id).first_or_404()
	title  = test.time

	results = Result.query.filter_by(test_id=test.id).order_by(Result.vm_name)

	av_list = []
	hcolumns = [ u'name' ]

	hresults = []
	hres = {}

	for res in results:
		if res.vm_name not in av_list:
			av_list.append(res.vm_name)
		if res.kind not in hcolumns:
			hcolumns.append(res.kind)
		hres['name'] = res.vm_name
		hres[res.kind] = res.result
		hresults.append(hres)

	print "hcolumns: %s" % hcolumns
	print "av_list: %s" % av_list

	reports = []

	for av in av_list:
		res = Result.query.filter_by(vm_name=av,test_id=test.id)
		report = {}
		report['name'] = av
		report['results'] = {}

		for r in res:
			if "END" in r.result.split(", ")[-1]: 
				report['results'][r.kind] = [ t_id, r.id, r.result.split(", ")[-2] ]
			else: 
				report['results'][r.kind] = [ t_id, r.id, r.result.split(", ")[-1] ]

		print report
		reports.append(report)

	return render_template("report.html", title=title, av_list=av_list, hcolumns=hcolumns, reports=reports)

if __name__ == "__main__":
	
	init_db(DB_PATH)
	app.run(host='0.0.0.0', port=8000)
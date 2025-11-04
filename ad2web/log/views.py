# -*- coding: utf-8 -*-

import os
import numbers
import html

from flask import Blueprint, render_template, abort, g, request, flash, Response, url_for, redirect
from flask import current_app as APP
from flask_login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required
from .constants import ARM, DISARM, POWER_CHANGED, ALARM, FIRE, BYPASS, BOOT, \
                        CONFIG_RECEIVED, ZONE_FAULT, ZONE_RESTORE, LOW_BATTERY, \
                        PANIC, EVENT_TYPES, LRR, READY, CHIME, RFX, EXP, AUI
from .models import EventLogEntry
from ..logwatch import LogWatcher
from ..utils import INSTANCE_FOLDER_PATH

import json
import collections

log = Blueprint('log', __name__, url_prefix='/log')


@log.context_processor
def log_context_processor():
    return {
        'ARM': ARM,
        'DISARM': DISARM,
        'POWER_CHANGED': POWER_CHANGED,
        'ALARM': ALARM,
        'FIRE': FIRE,
        'BYPASS': BYPASS,
        'BOOT': BOOT,
        'CONFIG_RECEIVED': CONFIG_RECEIVED,
        'ZONE_FAULT': ZONE_FAULT,
        'ZONE_RESTORE': ZONE_RESTORE,
        'LOW_BATTERY': LOW_BATTERY,
        'PANIC': PANIC,
        'LRR': LRR,
        'READY': READY,
        'EXP': EXP,
        'RFX': RFX,
        'AUI': AUI,
        'TYPES': EVENT_TYPES
    }

@log.route('/')
@login_required
def events():
#    event_log = None #EventLogEntry.query.order_by(EventLogEntry.timestamp.desc()).limit(50)

    return render_template('log/events.html', active="events")

@log.route('/live')
@login_required
@admin_required
def live():
    return render_template('log/live.html', active='live')

@log.route('/delete')
@login_required
@admin_required
def delete():
    events = EventLogEntry.query.delete()
    db.session.commit()
    return redirect(url_for('log.events'))

@log.route('/alarmdecoder')
@login_required
@admin_required
def alarmdecoder_logfile():
    return render_template('log/alarmdecoder.html', active='AlarmDecoder')

@log.route('/alarmdecoder/get_data/<int:lines>', methods=['GET'])
@login_required
@admin_required
def get_log_data(lines):
    log_file = os.path.join(INSTANCE_FOLDER_PATH, "logs", "info.log")
    try:
        log_text = LogWatcher.tail(log_file, lines)
    except IOError as err:
        return json.dumps([str(err)])
    return json.dumps(log_text)

#XHR for retrieving event log data server side
@log.route('/retrieve_events_paging_data')
@login_required
def get_events_paging_data():
    results = {}

    try:
        #get results from datatable via XHR
        results = DataTablesServer(request).output_result()
    except TypeError as ex:
        APP.logger.warning("Error processing datatables request: {0}".format(ex))

    return json.dumps(results)

class DataTablesServer:
    def __init__( self, request ):
        #values specified by datatable for filtering, sorting, paging etc
        self.request_values = request.values
        self.result_data = None

        #total in table unfiltered
        self.cardinality = 0
        #total in table after filter
        self.cardinality_filtered = 0
        
        self.run_queries()

    def output_result(self):
        output = {}
        output['sEcho'] = html.escape(str(int(self.request_values['sEcho'])))
        output['iTotalRecords'] = int(self.cardinality);
        output['iTotalDisplayRecords'] = int(self.cardinality);

        aaData_rows = []

        #iterate the result and append data rows
        for row in self.result_data:
            aaData_row = []
            aaData_row.append(str(row.timestamp))
            aaData_row.append(EVENT_TYPES[row.type])
            aaData_row.append(row.message)

            aaData_rows.append(aaData_row)

        output['aaData'] = aaData_rows
        return output

    def run_queries(self):
        pages = self.paging()
        search_filter = self.filtering()

        start = pages.start or 0
        limit = pages.length or 10

        try:
            if search_filter:
                query = EventLogEntry.query.filter(EventLogEntry.message.like(f"%{search_filter}%"))
                self.result_data = (
                    query.order_by(EventLogEntry.timestamp.desc()).limit(limit).offset(start)
                )
                self.cardinality_filtered = query.count()
                self.cardinality = query.count()
            else:
                query = EventLogEntry.query.order_by(EventLogEntry.timestamp.desc())
                self.result_data = query.limit(limit).offset(start)
                self.cardinality_filtered = query.count()
                self.cardinality = query.count()
        except Exception as e:
            APP.logger.error(f"Error querying event logs: {e}")

    #here we determine the filter value for the search box and apply to the queries
    def filtering(self):
        filter = None
        if( 'sSearch' in self.request_values) and (self.request_values['sSearch'] != "" ):
            filter = html.escape(str(self.request_values['sSearch']))

        return filter

    #determine what page we're on, as well as how many to show per page
    def paging(self):
        pages = collections.namedtuple('pages', ['start', 'length'])
        if( self.request_values['iDisplayStart'] != "" ) and (self.request_values['iDisplayLength'] != -1 ):
            if self.request_values['iDisplayStart'].isdigit() is False or self.request_values['iDisplayLength'].isdigit() is False:
                return pages

            pages.start = int(html.escape(self.request_values['iDisplayStart']))
            pages.length = int(html.escape(self.request_values['iDisplayLength']))

        return pages

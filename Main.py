import threading
import time
from flask_toastr import Toastr
from flask_wtf import CSRFProtect 
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, current_app

from Backend.Logs import logs
from Backend.Notion import Notion
from Backend.GoogleTasks import GoogleTasks

from config import frontend, backend

app = Flask(__name__)

#auto sync function
#runs in a thread
#runs every AUTO_SYNC_TIME seconds
#syncs google tasks to notion automatically
def autoSync():
    while True: #do this forever
        try:
            webLogs.infoLogs.info("Auto Syncing...") #info log

            status=google.get_google_tasks() #get google tasks
            tasks=status[0] #tasks list
            status=status[1] #status True/False

            #sync to notion
            status=notion.add_tasks_to_notion(tasks,backend.NOTION_DATABASE_ID,True)
        except: #if any error occurs, then log it
            webLogs.errorLogs.error("Auto Sync stopped")
        
        #sleep for AUTO_SYNC_TIME seconds, by default 30 seconds
        time.sleep(backend.AUTO_SYNC_TIME)

#auto sync thread
auto_sync_thread=threading.Thread(target=autoSync)

class Main:
    def __init__(self):
        pass

    #main function to run the server, default port is 5000
    def run(self,port=5000):
        webLogs.infoLogs.info("Starting server on port "+str(port))
        app.run(port=port) #run the server



    #---------------------------------------------------------------------------------------------------------#
    #Web Routes
        

    #default route/url
    #this is the main page of the website
    @app.route("/")
    def Index():
        try:
            webLogs.infoLogs.info("Index page loaded") #info log
            return render_template('public/index.html', frontend=frontend)
        except Exception as e:
            webLogs.errorLogs.error("Error in Index: "+str(e)) #error log
            return render_template('error/500.html', frontend=frontend), 500
        
    #route to handle google oauth
    #click on the google button on the index page to redirect to this route
    @app.route("/LinkGoogle")
    def LinkGoogle():
        try:
            webLogs.infoLogs.info('Linking Google Account...')
    
            #check if google account is already linked
            if session.get('googleAccountLinked')==1:
                flash("Google Account Already Linked!", 'info')
                webLogs.infoLogs.info("Google Account Already Linked")
                return redirect(url_for('Index'))

            #if not, then link the google account
            status=google.link_google_account()

            #if not able to link google account, then return error
            if not status:
                flash("Unable to Link Google Account!", 'error')
                webLogs.errorLogs.error("Unable to Link Google Account")
                return redirect(url_for('Index'))

            #if AUTO_SYNC is alive, then stop/join it
            if auto_sync_thread.is_alive():
                auto_sync_thread.join()

            #start the auto sync thread
            auto_sync_thread.start()

            #set the session variable to 1
            session['googleAccountLinked']=1


            flash("Google Account Linked!", 'info')
            webLogs.infoLogs.info("Google Account Linked")
            flash("Auto Syncing Started!", 'info')

            return redirect(url_for('Index'))
        except Exception as e: #if any error occurs, then return 500 error page
            webLogs.errorLogs.error("Error in LinkGoogle: "+str(e))
            return render_template('error/500.html', frontend=frontend), 500
        
    #route to unlink google account
    #click on the unlink button on the index page to redirect to this route
    @app.route("/UnlinkGoogle")
    def UnlinkGoogle():
        try:
            webLogs.infoLogs.info('Unlinking Google Account...')

            #unlink google account
            status=google.revoke_google_access()

            #if not able to unlink google account, then return error
            if not status:
                flash("Unable to Unlink Google Account!", 'error')
                webLogs.errorLogs.error("Unable to Unlink Google Account")
                return redirect(url_for('Index'))

            #set session variable to 0
            session['googleAccountLinked']=0

            flash("Google Account Unlinked!", 'info')
            webLogs.infoLogs.info("Google Account Unlinked")

            return redirect(url_for('Index'))
        except Exception as e: #if any error occurs, then return 500 error page
            webLogs.errorLogs.error("Error in UnlinkGoogle: "+str(e))
            return render_template('error/500.html', frontend=frontend), 500

    #route to sync google tasks to notion manually
    #click on the manual sync button on the index page to redirect to this route
    @app.route("/Sync")
    def Sync():
        try:
            webLogs.infoLogs.info('Syncing Google Tasks to Notion...')
    
            #check if google account is linked, if not then return error
            if session.get('googleAccountLinked')==0:
                flash("Google Account Not Linked!", 'error')
                webLogs.errorLogs.error("Google Account Not Linked")
                return redirect(url_for('Index'))

            #get google tasks
            status=google.get_google_tasks()

            tasks=status[0] #tasks list
            status=status[1] #status True/False

            #if not able to get google tasks, then return error, set session variable to 0 and revoke google access
            if not status:
                flash("Google Tasks Credentials Expired!", 'error')
                session['googleAccountLinked']=0 #set session variable to 0
                google.revoke_google_access() #revoke google access
                webLogs.errorLogs.error("Credentials not available or expired")
                return redirect(url_for('Index'))
            
            #add tasks to notion, pass database id and True for auto sync, False for manual sync (just for logging purpose)
            status=notion.add_tasks_to_notion(tasks,backend.NOTION_DATABASE_ID,False)

            #if not able to add tasks to notion, then return error
            if not status:
                flash("Unable to Sync tasks to Notion!", 'error')
                webLogs.errorLogs.error("Unable to Sync Google Tasks to Notion")
                return redirect(url_for('Index'))

            flash("Google Tasks Synced to Notion Manually!", 'info')
            webLogs.infoLogs.info("Google Tasks Synced to Notion")

            return redirect(url_for('Index'))
        except Exception as e: #if any error occurs, then return 500 error page
           webLogs.errorLogs.error("Error in Sync: "+str(e))
           return render_template('error/500.html', frontend=frontend), 500

    #---------------------------------------------------------------------------------------------------------#
    #Error Handling Routes

    #default 404 error handler
    @app.errorhandler(404)
    def error404(e):
        webLogs.errorLogs.error("Error 404: "+str(e))
        return render_template('error/404.html', frontend=frontend), 404
    
    #default 500 error handler
    @app.errorhandler(500)
    def error500(e):
        webLogs.errorLogs.error("Error 500: "+str(e))
        return render_template('error/500.html', frontend=frontend), 500


if __name__ == "__main__":
    toastr = Toastr(app) #for flash messages

    frontend=frontend() #frontend variables defined in config.py
    backend=backend() #backend variables defined in config.py

    app.secret_key = backend.SECRET_KEY #for session

    webLogs=logs(backend.WEB_LOGGING_PATH) #for logging

    google=GoogleTasks(backend) #google tasks object
    notion=Notion(backend) #notion object

    Main().run() #run the server


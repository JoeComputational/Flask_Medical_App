import os
from datetime import datetime


class Logger():
    """ Module to manage application logs """
    appName = ''
    logType = ''
    debugMode = False
    printlog = None
    logfolder = "logs"

    @classmethod
    def init(cls, app_name, logType='s', debug_mode=False):
        ''' manage logging in an application
            @param: app_name    --> name of the application
            @param: logType     s --> standard --> print logs to both terminal and file
                                f --> file     --> print logs to log file only
                                t --> terminal --> print logs to terminal only 
            @param: debug_mode  --> print debug logs as well if set to True
        '''
        cls.appName = app_name
        cls.logType = logType
        cls.debugMode = debug_mode

        if logType == 'f':
            cls.printlog = cls._print_to_file

        elif logType == 't':
            cls.printlog = cls._print_to_terminal

        else:
            cls.printlog = cls._print_stanard

        if not os.path.exists(cls.logfolder):
            os.makedirs(cls.logfolder)

    @classmethod
    def _dayspan(cls, filename):
        datestr = filename.replace(".log", "").split("_")[-1]
        return (datetime.now() - datetime.strptime(datestr, '%Y%m%d%H')).days

    @classmethod
    def remove_logfiles(cls, days=5):
        """ remove log files after specified days span
            @param:days -> number of days to hold log files
        """
        files = os.listdir(cls.logfolder)
        files_to_remove = list(
            filter(lambda file: cls._dayspan(file) > days, files))
        for file in files_to_remove:
            try:
                os.remove(os.path.join(cls.logfolder, file))
            except:
                pass

    @classmethod
    def _print_to_file(cls, message):
        try:
            ds = datetime.now().strftime('%Y%m%d%H')
            file_path = f'{cls.appName}_{ds}.log'
            with open(os.path.join(cls.logfolder, file_path), 'a') as fp:
                fp.write(f'{message}\n')

        except Exception as e:
            print('Failed To Open Log File')

    @classmethod
    def _print_to_terminal(cls, message):
        print(message)

    @classmethod
    def _print_stanard(cls, message):
        cls._print_to_terminal(message)
        cls._print_to_file(message)

    @classmethod
    def exception(cls, e, occuredAt, id='', debug=False):
        extras = f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}]"
        message = f'{extras}[EXCEPTION]@{occuredAt} --> {e}' if id == '' else f'[EXCEPTION_{id}]@{occuredAt} --> {e}'

        if debug:
            if cls.debugMode:
                cls.printlog(message)

        else:
            cls.printlog(message)

    @classmethod
    def info(cls, message, debug=False):
        extras = f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}]"
        message = f'{extras}[INFO] {message}'

        if debug:
            if cls.debugMode:
                cls.printlog(message)

        else:
            cls.printlog(message)

    @classmethod
    def error(cls, message, debug=False):
        extras = f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}]"
        message = f'{extras}[ERROR] {message}'

        if debug:
            if cls.debugMode:
                cls.printlog(message)

        else:
            cls.printlog(message)

    @classmethod
    def debug(cls, message):
        if cls.debugMode:
            cls.printlog(f"[ DEBUG ] {message}")

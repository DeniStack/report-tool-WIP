#for error log app
def build_db_query_string_app5(language):
    language = language.lower()
    db_query_string = """SELECT FailureDescription.ID,
                            FailureDescription.[Alarm text  de-DE , Alarm text],
                            --NotificationLog.FailureCode, 
                            NotificationLog.Timestamp,
							NotificationLog.Duration
                            FROM NotificationLog, FailureDescription
                            WHERE NotificationLog.Timestamp
                            BETWEEN ? AND ?
                            AND FailureDescription.ID = NotificationLog.FailureCode;"""
    return db_query_string

 #for downtime log app
def build_db_query_app7():
    db_query_string = """SELECT NotificationLog.ID as 'ID',
                        NotificationLog.Timestamp,
                        NotificationLog.Duration,
                        DATEPART(WEEK, NotificationLog.Timestamp)-1 as 'Week Number'
                        FROM NotificationLog
                        WHERE NotificationLog.Timestamp
                            BETWEEN ? AND ?"""
    return db_query_string

import MySQLdb

class db_api(object):
    def __init__(self):
        """
        parse configuration
        """
        self.hostip = "127.0.0.1"
        self.user = "root"
        self.passwd = ""
        self.dbname = "myboly"
        self.tablelsp = "lsp"   # modify to health later
        self.tableflow = "flow"   # modify to health later
        self.port = 3306
        self.charset ="utf8"

    def conn(self):
        """
        connecting to the database
        """
        try:
            conn = MySQLdb.connect(host=self.hostip, user=self.user,
                                   passwd=self.passwd, db=self.dbname,
                                   port=int(self.port), charset=self.charset)
            conn.ping(True)
            return conn
        except MySQLdb.Error, e:
            error_msg = 'Error {}: {}'.format(e.args[0], e.args[1])
            print error_msg

    def disconnect(self):
        conn = self.conn()
        conn.close()

    def get_healthest_lsp(self):
        try:
            conn = self.conn()
            cur = conn.cursor()

            #cur.execute("select lsp from {}".format(self.tablelsp))
            #res = int(cur.fetchone()[0])
            # TODO work on the lsp healthest selection

            return 1
        except Exception, e:
            print str(e)
            return -1

    def update_health(self, lsp, latency, loss):
        try:
            conn = self.conn()
            cur = conn.cursor()
            
            cur.execute("update {} \
                         set latency={},\
                         loss_rate={}\
                         where id={} or id={}".format(self.tablelsp,
                                                      latency, loss,
                                                      lsp+1, lsp+5))
            conn.commit()
            conn.close()
            return True
        except Exception, e:
            print str(e)
            return False

if __name__ == "__main__":
    cc = db_api()
    print cc.update_health(2, 200, 55.0) 

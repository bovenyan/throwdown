import MySQLdb
import datetime

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

            return 2
        except Exception, e:
            print str(e)
            return -1

    def get_lsp_metrix(self, lsp):
        try:
            conn = self.conn()
            cur = conn.cursor()

            cur.execute("select latency,\
                         loss_rate, bandwidth,\
                         utility, flow_no, last_redis_update\
                         from {} \
                         where id={}".format(self.tablelsp,
                                             lsp+1))
            res=cur.fetchone()
            cur.close()
            return res
        except Exception, e:
            print str(e)
            return None

    def register_flow(self, proto, src_port, dst_port, qos, app_id):
        try:
            conn = self.conn()
            cur = conn.cursor()

            cur.execute("insert into {} (protocol, src_port, \
                          dst_port, qos_type, app_id)\
                          values ({}, {}, {}, {}, {})".format(self.tableflow,
                                                              proto, src_port,
                                                              dst_port, qos,
                                                              ))
            conn.commit()
            conn.close()
            return True
        except Exception, e:
            print str(e)
            return None

    def check_registered_qos(self, proto, src_port, dst_port):
        try:
            conn = self.conn()
            cur = conn.cursor()

            cur.execute("select qos_type from {} \
                         where protocol={} and src_port={} and \
                         dst_port={}".format(self.tableflow,
                                             proto, src_port,
                                             dst_port))
            res = cur.fetchone()
            
            if res is None:
                return None
            else:
                return int(res)

        except Exception, e:
            print str(e)
            return None

    def commit_flow(self, cookie, lsp, proto, src_port, dst_port,
                    qos_type, app_id=0):
        try:
            conn = self.conn()
            cur = conn.cursor()
            cur.execute("insert into {} (cookie, protocol, \
                         src_port, dst_port, lsp, qos_type, app_id)\
                         values ({}, {}, {}, {}, {}, {}, \
                         {}) on duplicate key update lsp={}, qos_type={},\
                         app_id={}".format(self.tableflow, cookie, proto,
                                            src_port, dst_port, lsp+1,
                                            qos_type, app_id,
                                            lsp+1, qos_type, app_id))
            conn.commit()
            conn.close()
            return True

        except Exception, e:
            print str(e)
            return False

    def unavailable_lsps(self, app_id, reverse):
        try:
            conn = self.conn()
            cur = conn.cursor()
            if reverse:
                cur.execute("select lsp-5 from {} where \
                            app_id={} and lsp > 4".format(self.tableflow,
                                                          app_id))
            else:
                cur.execute("select lsp-1 from {} where \
                            app_id={} and lsp < 5".format(self.tableflow,
                                                          app_id))
            res=cur.fetchall()
            res_parsed = []
            for i in range(len(res)):
                res_parsed.append(res[i][0])
            return res
        except Exception, e:
            print str(e)
            return []

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

    def get_flows(self):
        try:
            conn = self.conn()
            cur = conn.cursor()

            cur.execute("select cookie from {}".format(self.tableflow))

            res=cur.fetchall()
            res_parsed = []
            for i in range(len(res)):
                res_parsed.append(res[i][0])
            return res
        except Exception, e:
            print str(e)
            return []

    def delete_flows(self, cookies):
        try:
            conn = self.conn()
            for cookie in cookies:
                cur = conn.cursor()
                cur.execute("delete from {} where cookie={}".format(
                    self.tableflow, cookies[i]))
                conn.commit()
            conn.close()
        except Exception, e:
            print str(e)
            return False

if __name__ == "__main__":
    cc = db_api()
    # print cc.update_health(2, 200, 55.0)
    print cc.check_registered_flow(6, 80, 1000)

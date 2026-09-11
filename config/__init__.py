# Config initialization for CampusPulse AI
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

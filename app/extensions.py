from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles
from flask_socketio import SocketIO
from flask_cache import Cache
from flask_uploads import UploadSet

jwt = JWTManager()
db = SQLAlchemy()
mail = Mail()
socket = SocketIO()
cache = Cache()
# attachments = UploadSet('ATTACHMENTS', extensions='up_files')


# SQLAlchemy does not map BigInt to Int by default on the sqlite dialect.
# It should, but it doesnt.
class SLBigInteger(BigInteger):
    pass


@compiles(SLBigInteger, 'sqlite')
def bi_c1(element, compiler, **kw):
    return "INTEGER"


@compiles(SLBigInteger)
def bi_c2(element, compiler, **kw):
    return compiler.visit_BIGINT(element, **kw)

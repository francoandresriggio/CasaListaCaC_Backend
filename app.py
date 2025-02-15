from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)

CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://FrancoRiggio:codoacodo@FrancoRiggio.mysql.pythonanywhere-services.com/FrancoRiggio$default'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Profesion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profesion = db.Column(db.String(100))

    #Relaciones
    profesion_usuario = db.relationship('Usuarios', backref='profesion', lazy=True)

    def __init__(self, profesion):
        self.profesion = profesion

class Usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    mail = db.Column(db.String(50), nullable=False)
    contrasena = db.Column(db.String(128), nullable=False)
    zona = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.Integer, nullable=False)
    genero = db.Column(db.String(4), nullable=False)
    imagen = db.Column(db.String(1000), nullable=False)
    profesion_id = db.Column(db.Integer, db.ForeignKey('profesion.id'))
    valoracion_media_profesional = db.Column(db.Numeric(precision=3, scale=2))
    descripcion_profesional = db.Column(db.String(1000))

    #Relaciones
    pedidos_realizados = db.relationship('Pedidos', foreign_keys='Pedidos.cliente_id', backref='cliente', lazy=True)
    pedidos_recibidos = db.relationship('Pedidos', foreign_keys='Pedidos.profesional_id', backref='profesional', lazy=True)

    pedido_evaluado_cliente = db.relationship('Valoracion', foreign_keys='Valoracion.cliente_id', backref='cliente', lazy=True)
    pedido_evaluado_profesional = db.relationship('Valoracion', foreign_keys='Valoracion.profesional_id', backref='profesional', lazy=True)

    def __init__(self, nombre, apellido, mail, contrasena, zona, telefono, genero, imagen):
        self.nombre = nombre
        self.apellido = apellido
        self.mail = mail
        self.contrasena = contrasena
        self.zona = zona
        self.telefono = telefono
        self.genero = genero
        self.imagen = imagen

class Pedidos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    profesional_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha_realizado = db.Column(db.DateTime)

    def __init__(self, cliente_id, profesional_id):
        self.cliente_id = cliente_id
        self.profesional_id = profesional_id

class Valoracion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    profesional_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    valoracion_media_individual = db.Column(db.Numeric(precision=3, scale=2))
    comentario = db.Column(db.String(400), nullable=False)

    def __init__(self, cliente_id, profesional_id, valoracion_media_individual, comentario):
        self.cliente_id = cliente_id
        self.profesional_id = profesional_id
        self.valoracion_media_individual = valoracion_media_individual
        self.comentario = comentario

with app.app_context():
    db.create_all()

    listado_profesiones = Profesion.query.all()

    if len(listado_profesiones) == 0:
        profesiones = ["Electricista", "Gasista", "Plomero", "Carpintero", "Jardinero", "Cerrajero", "Aire acondicionado", "Pintor", "Albañil", "Fletero"]

        for agregar_profesion in profesiones:
            nueva_profesion = Profesion(profesion=agregar_profesion)
            db.session.add(nueva_profesion)
            db.session.commit()

@app.route("/")
def index():
    return 'App Web de CasaLista'


@app.route("/altaUsuario", methods=['POST'])
def alta_usuario():

    nombre = request.json["nombre"]
    apellido = request.json["apellido"]
    mail = request.json["mail"]
    zona = request.json["zona"]
    telefono = request.json["telefono"]
    genero = request.json["genero"]
    imagen = request.json["imagen"]
    contrasena = request.json["contrasena"]

    nuevo_usuario = Usuarios(nombre=nombre, apellido=apellido, mail=mail, zona=zona, telefono=telefono, genero=genero, imagen=imagen, contrasena=contrasena)
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({
        'id': nuevo_usuario.id
    }), 201

@app.route("/consultaUsuario/<id>", methods=['GET'])
def consulta_usuario(id):
    usuario_consulta = Usuarios.query.get(id)

    usuario_profesion = None

    if usuario_consulta.profesion_id is not None:
        usuario_profesion = usuario_consulta.profesion.profesion

    return jsonify({
        'id': usuario_consulta.id,
        'nombre': usuario_consulta.nombre,
        'apellido': usuario_consulta.apellido,
        'mail': usuario_consulta.mail,
        'zona': usuario_consulta.zona,
        'telefono': usuario_consulta.telefono,
        'genero': usuario_consulta.genero,
        'imagen': usuario_consulta.imagen,
        'contrasena': usuario_consulta.contrasena,
        'profesion': usuario_profesion,
        'descripcion_profesion': usuario_consulta.descripcion_profesional
    }), 200

@app.route("/correoExistente", methods=['GET'])
def usuario_existente():
    mail_usuario = request.args.get("mail")
    usuario_consulta = Usuarios.query.filter_by(mail=mail_usuario).first()

    if usuario_consulta is None:
        return jsonify({'existe': False}), 200
    else:
        return jsonify({'existe': True}), 200


@app.route("/loginUsuario", methods=['POST'])
def login_usuario():
    data = request.get_json()

    mail = data["mail"]
    contrasena = data["contrasena"]

    usuario = Usuarios.query.filter_by(mail=mail).first()

    if not usuario or usuario.contrasena != contrasena:
        return jsonify({'mensaje': 'usuario y/o contraseña no válidos'}), 401

    return jsonify({
            'mensaje': 'inicio exitoso',
            'id': usuario.id
    }), 200


@app.route('/actualizarPerfil/<id>', methods=['PUT'])
def update(id):
    usuario = Usuarios.query.get(id)

    mail = request.json["mail"]
    nombre = request.json["nombre"]
    apellido = request.json["apellido"]
    zona = request.json["zona"]
    genero = request.json["genero"]
    telefono = request.json["telefono"]
    imagen = request.json["imagen"]
    contrasena = request.json["contrasena"]

    profesion_nombre = request.json["profesion"]

    descripcion_profesional = request.json["descripcion"]

    if profesion_nombre is not None:
        profesion = Profesion.query.filter_by(profesion=profesion_nombre).first()
        usuario.profesion_id = profesion.id
        usuario.descripcion_profesional = descripcion_profesional
    else:
        usuario.profesion_id = None
        usuario.descripcion_profesional = None

    usuario.mail = mail
    usuario.nombre = nombre
    usuario.apellido = apellido
    usuario.zona = zona
    usuario.genero = genero
    usuario.telefono = telefono
    usuario.imagen = imagen
    usuario.contrasena = contrasena

    db.session.commit()

    return jsonify({
            'mensaje': 'Datos actualizados correctamente'
    }), 200


@app.route('/solicitarEspecialistas/<id>', methods=['GET'])
def listado_especialistas(id):
    especialistas = Usuarios.query.filter(Usuarios.profesion_id.isnot(None)).all()
    listado_especialistas = []

    for especialista in especialistas:
        if especialista.id != int(id):
            profesion = Profesion.query.filter_by(id=especialista.profesion_id).first()
            valoracion_media = especialista.valoracion_media_profesional
            if valoracion_media is None:
                valoracion_media = 0

            listado_especialistas.append({
                'id': especialista.id,
                'nombre': especialista.nombre,
                'apellido': especialista.apellido,
                'telefono': especialista.telefono,
                'zona': especialista.zona,
                'foto_perfil': especialista.imagen,
                'profesion': profesion.profesion,
                'descripcion': especialista.descripcion_profesional,
                'valoracion': valoracion_media
            })

    return jsonify(listado_especialistas), 200


@app.route("/altaPedido", methods=['POST'])
def alta_pedido():
    cliente_id = request.json["clienteId"]
    profesional_id = request.json["profesionalId"]

    nuevo_pedido = Pedidos(cliente_id=cliente_id, profesional_id=profesional_id)
    db.session.add(nuevo_pedido)
    db.session.commit()

    return "Solicitud de alta recibida", 201


@app.route('/solicitarPedidos/<id>', methods=['GET'])
def listado_pedidos(id):
    pedidos = Pedidos.query.filter_by(profesional_id=int(id)).all()
    listado_pedidos = []

    for pedido in pedidos:
        if pedido.fecha_realizado is None:
            cliente_pedido = Usuarios.query.get(pedido.cliente_id)
            listado_pedidos.append({
                "id": pedido.id,
                "nombre": cliente_pedido.nombre,
                "apellido": cliente_pedido.apellido,
                "foto_perfil": cliente_pedido.imagen,
                "telefono": cliente_pedido.telefono
            })

    return jsonify(listado_pedidos), 200


@app.route('/pedidoRealizado/<id>', methods=['PUT'])
def pedido_realizado(id):
    pedido = Pedidos.query.get(id)
    pedido.fecha_realizado = datetime.now()
    db.session.commit()

    return "Trabajo realizado", 200

@app.route('/solicitarHistorial/<id>', methods=['GET'])
def listado_historial(id):
    pedidos = Pedidos.query.filter_by(cliente_id=int(id)).all()

    listado_historial = []

    for pedido in pedidos:
        if pedido.fecha_realizado is not None:
            profesional_pedido = Usuarios.query.get(pedido.profesional_id)

            fecha_pedido_realizado = f'{pedido.fecha_realizado.day}/{pedido.fecha_realizado.month}/{pedido.fecha_realizado.year}'

            profesion = Profesion.query.filter_by(id=profesional_pedido.profesion_id).first().profesion

            listado_historial.append({
                "id_pedido": pedido.id,
                "nombre": profesional_pedido.nombre,
                "apellido": profesional_pedido.apellido,
                "foto_perfil": profesional_pedido.imagen,
                "fecha_trabajo": fecha_pedido_realizado,
                "profesion": profesion
            })

    return jsonify(listado_historial), 200

@app.route('/solicitarEspecialistaHistorial/<id>', methods=['GET'])
def listado_historial_especialista(id):
     pedido = Pedidos.query.get(id)

     profesional = Usuarios.query.get(pedido.profesional_id)
     profesion = Profesion.query.filter_by(id=profesional.profesion_id).first().profesion

     return jsonify({
            'id_profesional': profesional.id,
            'nombre': profesional.nombre,
            'apellido': profesional.apellido,
            'foto_perfil': profesional.imagen,
            'profesion': profesion
    }), 200


@app.route("/nuevaValoracion", methods=['POST'])
def nueva_valoracion_usuario():
    amabilidad = int(request.json["amabilidad"])
    puntualidad = int(request.json["puntualidad"])
    proligidad = int(request.json["proligidad"])
    confiabilidad = int(request.json["confiabilidad"])
    comentarios = request.json["comentarios"]
    cliente = request.json["cliente_id"]
    profesional = request.json["profesional_id"]

    nueva_valoracion = Valoracion(cliente_id=cliente, profesional_id=profesional, valoracion_media_individual=(amabilidad+puntualidad+proligidad+confiabilidad)/4, comentario=comentarios)

    db.session.add(nueva_valoracion)
    db.session.commit()

    valoracion_media = 0

    valoraciones = Valoracion.query.filter_by(profesional_id=profesional).all()

    for valoracion in valoraciones:
        valoracion_media += valoracion.valoracion_media_individual

    valoracion_media /= len(valoraciones)

    profesional = Usuarios.query.get(profesional)
    profesional.valoracion_media_profesional = valoracion_media
    db.session.commit()

    return "Trabajo evaluado", 200


@app.route('/borrarPedidoHistorial/<id>', methods=['DELETE'])
def borrar(id):

    pedido = Pedidos.query.get(id)

    db.session.delete(pedido)
    db.session.commit()

    return "Pedido eliminado"

@app.route('/solicitarEspecialistaComentarios/<id>', methods=['GET'])
def listado_comentarios_especialista(id):
    especialista_valoraciones = Valoracion.query.filter_by(profesional_id=int(id)).all()

    comentarios_especialista = []

    for especialista_valoracion in especialista_valoraciones:
        cliente_comentario = Usuarios.query.get(especialista_valoracion.cliente_id)
        comentarios_especialista.append({
            'nombre_comentario': cliente_comentario.nombre + " " + cliente_comentario.apellido,
            'comentario': especialista_valoracion.comentario
        })

    return jsonify(comentarios_especialista), 200
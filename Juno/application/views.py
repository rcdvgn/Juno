from flask import *
from datetime import timedelta
from . modelo import *
import mysql.connector
import hashlib
from datetime import datetime

mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root"
)

db = mydb.cursor()

views = Blueprint('views', __name__)

@views.before_request
def session_lifetime():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=365)

def novo_usuario(username, senha, email):
    erro, erro1, erro2, erro3 = "", "", "", ""

    if len(username) == 0 or len(senha) == 0 or len(email) == 0:
        erro = "Preencha todos os campos."
    # ----------------------------------------------------------------------------
    db.execute(f"SELECT * FROM juno.usuarios WHERE email = '{email}';")
    dbemail = db.fetchone()
    if dbemail:
        erro1 = "Email ja cadastrado."
    # ----------------------------------------------------------------------------   
    if username[0].isnumeric():
        erro2 = "Nome de usuario nao pode comecar em numeros."
    if " " in username:
        erro2 = "Nome de usuario nao pode conter espacos."
    elif len(username) > 20:
        erro2 = "Nome de usuario muito longo, limite: 20 caracteres."

    db.execute(f"SELECT * FROM juno.usuarios WHERE username = '{username}';")
    usuario = db.fetchone()
    if usuario:
        erro2 = "Nome de usuario ja cadastrado."
    # ----------------------------------------------------------------------------
    if " " in senha:
        erro3 = "Senha nao pode conter espacos."
    elif len(senha) > 20:
        erro3 = "Senha muito longa, limite: 20 caracteres."

    if erro == "" and erro1 == "" and erro2 == "" and erro3 == "":
        return True
    else:
        return erro, erro1, erro2, erro3



def entrar_usuario(username, senha):
    erro, erro1, erro2 = "", "", ""

    if len(username) == 0 or len(senha) == 0:
        erro = "Preencha todos os campos."
    # ----------------------------------------------------------------------------
    if " " in username:
        erro1 = "Nome de usuario nao pode conter espacos."
    elif len(username) > 20:
        erro1 = "Nome de usuario muito longo, limite: 20 caracteres."
    # ----------------------------------------------------------------------------
    if " " in senha:
        erro2 = "Senha nao pode conter espacos."
    elif len(senha) > 20:
        erro2 = "Senha muito longa, limite: 20 caracteres."

    

    if erro == "" and erro1 == "" and erro2 == "":
        db.execute(f"SELECT * FROM juno.usuarios WHERE username = '{username}' and senha = '{hashlib.sha256(senha.encode()).hexdigest()}';")
        conta = db.fetchone()
        if conta:
            session['username'] = conta[1]
            session['user_id'] = conta[0]
            session.modified = True
            return True
        else:
            erro = "Nome de usuario ou senha incorretos."
            return erro, erro1, erro2
    else:
        return erro, erro1, erro2


def existencia(ano):
    db.execute(f"SELECT * FROM juno.consultas WHERE uid = '{session['user_id']}' and ano = '{ano}';")
    consulta = db.fetchone()
    if consulta:
        return consulta[1], consulta[3], consulta[4]
    else:
        return False


def validacao(ano):
    if len(ano) > 10:
        return 'Entrada invalida'
    if not ano.isnumeric():
        return f'"{ano}" nao eh um ano...'
    ano = float(ano)
    if not ano.is_integer():
        return "Apenas anos inteiros serao considerados validos"
    ano = int(ano)
    if ano < 2023 or ano > 2099:
        return "Apenas anos entre 2023 e 2099 serao considerados validos"
    return True



@views.route("/")
def main():
    return redirect(url_for('views.consultas'))


@views.route("/saber-mais")
def saber_mais():
    return render_template('saber_mais.html')
    
@views.route("/entrar", methods=["GET", "POST"])
def entrar():
    if request.method =="POST":
        username = request.form['username']
        senha = request.form['senha']

        if entrar_usuario(username, senha) == True:
            return redirect(url_for('views.consultas'))
            
        else:
            erro, erro1, erro2 = entrar_usuario(username, senha)
            return render_template('entrar.html', erro=erro, erro1=erro1, erro2=erro2, username=username, senha=senha)

    else:
        session.pop('username', None)
        session.pop('user_id', None)
        session.modified = True
        return render_template('entrar.html')

@views.route("/criar-conta", methods=["GET", "POST"])
def criar_conta():
    if request.method =="POST":
        username = request.form['username']
        senha = request.form['senha']
        email = request.form['email']


        if novo_usuario(username, senha, email) == True:
            db.execute(f"INSERT INTO juno.usuarios(username, senha, email) VALUES('{username}', '{hashlib.sha256(senha.encode()).hexdigest()}', '{email}');")
            mydb.commit()

            return redirect(url_for('views.consultas'))
        else:
            erro, erro1, erro2, erro3 = novo_usuario(username, senha, email)
            return render_template('criar_conta.html', erro=erro, erro1=erro1, erro2=erro2, erro3=erro3, email=email, username=username, senha=senha)

        
        #return render_template('consultas.html', erro=f"{username}  {senha}  {email}")
    else:
        session.pop('username', None)
        session.pop('user_id', None)
        session.modified = True
        return render_template('criar_conta.html')

@views.route("/consultas/<ano>")
@views.route("/consultas/")
def consultas(ano=""):
    if 'username' in session:
        db.execute(f"SELECT ano, criacao FROM juno.consultas WHERE uid = '{session['user_id']}';")
        rows = db.fetchall()

        criacoes = []
        anos = []
        for row in rows:
            anos.append(row[0])
            if datetime.now().strftime("%d/%m/%Y") == row[1].split(" ")[0]:
                criacoes.append(row[1].split(" ")[1])
            else:
                criacoes.append(row[1].split(" ")[0])

        if ano == "":
            return render_template('consultas.html', status=0, anos=anos, criacoes=criacoes)
        else:
            if existencia(ano) == False:
                if validacao(ano) == True:
                    populacao, img = prever(int(ano), session['username'])
                    data = datetime.now().strftime("%d/%m/%Y")
                    hora = datetime.now().strftime("%H:%M")
                    criacao = f"{data} {hora}"
                    now = hora

                    db.execute(f"""INSERT INTO juno.consultas(uid, criacao, ano, populacao, img) VALUES('{session["user_id"]}', '{criacao}', '{ano}', '{populacao}', '{img}');""")
                    mydb.commit()

                    anos.append(ano)
                    criacoes.append(now)
                else:
                    return render_template('consultas.html', erro=validacao(ano), anos=anos, criacoes=criacoes)
            else:
                criacao, populacao, img = existencia(ano)
                if datetime.now().strftime("%d/%m/%Y") == criacao.split(" ")[0]:
                    now = criacao.split(" ")[1]
                else:
                    now = criacao.split(" ")[0]
                
            anos.reverse()
            criacoes.reverse()
            return render_template('consultas.html', status=1, ano=ano, populacao=populacao, img=img, now=now, anos=anos, criacoes=criacoes)
    else:
        return redirect(url_for('views.entrar'))




@views.route("/sair")
def sair():
    session.pop('username', None)
    session.pop('user_id', None)
    session.modified = True
    

    return redirect(url_for('views.entrar'))

from flask import Flask, render_template, url_for, request, redirect, session, escape, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc
from datetime import datetime
from flask_bootstrap import Bootstrap 
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
app.secret_key                                  = 'D@D@#G#$V'
app.config['SQLALCHEMY_DATABASE_URI'] 			= 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']    = False
db = SQLAlchemy(app)
Bootstrap(app)

class Admin(db.Model):
    id            	= db.Column(db.String(5), primary_key=True)
    username      	= db.Column(db.String(50))
    password      	= db.Column(db.Text)
    no_telp       	= db.Column(db.Text)
    alamat        	= db.Column(db.Text)
    email         	= db.Column(db.Text)
    date_created 	= db.Column(db.DateTime, default=datetime.utcnow)

class Petugas(db.Model):
    id            	= db.Column(db.String(10), primary_key=True)
    username      	= db.Column(db.String(50))
    jeniskelamin    = db.Column(db.String(50))
    password      	= db.Column(db.Text)
    no_telp       	= db.Column(db.Text)
    alamat        	= db.Column(db.Text)
    email         	= db.Column(db.Text)
    date_created 	= db.Column(db.DateTime, default=datetime.utcnow)

class Pelanggan(db.Model):
    id            	= db.Column(db.String(20), primary_key=True)
    nama          	= db.Column(db.String(50))
    alamat        	= db.Column(db.String(100))
    kota 			= db.Column(db.String(50))
    kec 			= db.Column(db.String(100))
    kdpos 			= db.Column(db.String(50))
    daya          	= db.Column(db.String(50))
    date_created 	= db.Column(db.DateTime, default=datetime.utcnow)

class Temuan(db.Model):
    id            	= db.Column(db.Integer, primary_key=True)
    petugas_id      = db.Column(db.String(10), db.ForeignKey('petugas.id'))
    pelanggan_id  	= db.Column(db.String(20), db.ForeignKey('pelanggan.id'))
    ket           	= db.Column(db.Text)
    status          = db.Column(db.String(50))
    lat             = db.Column(db.Float)
    lng             = db.Column(db.Float)
    date_created 	= db.Column(db.DateTime, default=datetime.utcnow)

class Tindakan(db.Model):
	id 				= db.Column(db.Integer, primary_key=True)
	temuan_id 		= db.Column(db.Integer, db.ForeignKey('temuan.id'))
	petugas_id      = db.Column(db.String(10), db.ForeignKey('petugas.id'))
	pelanggan_id  	= db.Column(db.String(20), db.ForeignKey('pelanggan.id'))
	ket           	= db.Column(db.Text)
	date_created 	= db.Column(db.DateTime, default=datetime.utcnow)


'''
now = datetime.now()
year = now.strftime("%y")
print("year", year)

month = now.strftime("%m")
print("month:", month)
day = now.strftime("%d")
print("day:", day)
time = now.strftime("%H:%M:%S")
print("time:", time)
date_time = now.strftime("%m/%d/%Y , %H:%M:%S")
print("date and time:",date_time)
jupan=datetime.utcnow
print("jam sekarang", jupan)
'''
def ValidasiLoginUser(Form):
	if Form:
		DataUser=Petugas.query.filter_by(id=Form['username'],password=Form['password']).first()
		if DataUser:
			session['user'] = {'username':DataUser.username,'id':DataUser.id}
			return {'error' : False, 'username':DataUser.username, 'message' : 'Berhasil Login'}
		else:
			return {'error' : True, 'message' : 'Gagal Login'}

def ValidasiLoginAdmin(Form):
	if Form:
		DataAdmin=Admin.query.filter_by(username=Form['username'],password=Form['password']).first()
		if DataAdmin:
			session['admin'] = {'username':DataAdmin.username,'id':DataAdmin.id}
			return {'error' : False, 'username':DataAdmin.username, 'message' : 'Berhasil Login'}
		else:
			return {'error' : True, 'message' : 'Gagal Login'}


#upload gambar
ALLOWED_EXTENSION = set(['png','jpg','jepg'])
app.config['UPLOAD_FOLDER'] = 'uploads'

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSION

@app.route('/uploadfile',methods=['GET','POST'])
def uploadfile():
	if request.method == 'POST':

		file = request.files['file']
		if 'file' not in request.files:
			return redirect(request.url)

		if file.filename == '':
			return redirect(request)

		if file and allowed_file(file.filename) :
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER']+filename))
			return ' file berhasil di save di ' + filename
	return render_template('upload.html')

@app.route('/', methods=['POST', 'GET'])
def index():
	return render_template('index.html')

@app.route("/userlog",methods=['POST','GET'])
def userlog():
    session.pop('user', None)
    validasi = ValidasiLoginUser(request.form)
    if request.method == 'POST':
        if validasi['error'] == False:
            username=request.form['username']
            flash('Berhasi log in','success')
            return redirect(url_for('user_home',username=username))
        return render_template('user_log.html', messagepesan="Username dan Password yang Anda Masukkan Salah")
    return render_template("user_log.html")


@app.route('/profile/<username>',methods=['GET','POST'])
def profile(username):
    user=Petugas.query.filter_by(username=username).first()
    if 'user' not in session:
        return redirect(url_for('login_user'))
    else:
        return render_template('user_profile.html',user=user)
        return 'oke'
    return 'oke'


@app.route("/adminlog",methods=['POST','GET'])
def adminlog():
	session.pop('admin', None)
	validasi = ValidasiLoginAdmin(request.form)
	if request.method == 'POST':
		if validasi['error'] == False:
			flash('Berhasi log in','success')
			return redirect(url_for('admin_admin'))
		return render_template('admin_log.html',messagepesan="Username dan Password yang Anda Masukkan Salah")
	return render_template("admin_log.html")

@app.route('/admin/admin')
def admin_admin():
	return render_template('admin_admin.html', title='Data Admin',container = Admin.query.all())


@app.route("/admin/petugas")
def admin_user():
	#if 'admin' not in session:
		#return redirect(url_for('index'))
	container = Petugas.query.order_by(desc(Petugas.date_created))
	return render_template('admin_user.html',title='Petugas', container = container)

@app.route('/admin/petugas/add', methods=['GET', 'POST'])
def admin_adduser():
	#if 'admin' not in session:
		#return redirect(url_for('index'))

    if request.method == 'POST':
    	reg	=request.form
    	nik= reg['nik']
    	username=reg['username']
    	jeniskelamin=reg['jenis_kelamin']
    	email=reg['email']
    	password=reg['password']
    	no_telp=reg['no_telp']
    	alamat=reg['alamat']
    	print(nik,username,jeniskelamin,email,password,no_telp,alamat)
    	AddPetugas  = Petugas(id=nik,username=username, jeniskelamin=jeniskelamin,email=email, password=password, no_telp=no_telp,alamat=alamat)
    	db.session.add(AddPetugas)
    	db.session.commit()
    	flash('Data Petugas Berhasil Disimpan','success')
    	#return ' data tersimpan'
    	return redirect(url_for('admin_user'))
    return render_template('admin_adduser.html')


@app.route('/admin/petugas/ubah/<id>', methods=['POST', 'GET'])
def admin_ubahuser(id):
    UbahUser= Petugas.query.filter_by(id=id).first()
    if request.method == 'POST':
        UbahUser.id = request.form['nik']
        UbahUser.username = request.form['username']
        UbahUser.jeniskelamin=request.form['jenis_kelamin']
        UbahUser.email = request.form['email']
        UbahUser.password = request.form['password']
        UbahUser.no_telp = request.form['no_telp']
        UbahUser.alamat = request.form['alamat']
        db.session.add(UbahUser)
        db.session.commit()
        flash('Data Petugas Berhasil Diedit','success')
        return redirect(url_for('admin_user'))
    else:
        return render_template('admin_ubahuser.html', user=UbahUser)


@app.route('/admin/petugas/hapus/<id>' , methods=['POST', 'GET'])
def admin_hapususer(id):
    HapusUser= Petugas.query.filter_by(id=id).first()
    db.session.delete(HapusUser)
    db.session.commit()
    flash('Data Petugas Berhasil Dihapus','success')
    return redirect(url_for('admin_user'))

@app.route('/admin/pelanggan',methods=['GET','POST'])
def admin_pelanggan():
	if request.method == 'POST':
		reg=request.form
		norek=reg['norek']
		user= Pelanggan.query.filter_by(id=norek).first()
		print(norek)
		#flash('Data Pelanggan Berhasil Disimpan','success')
		return render_template('admin_pelanggan_cari.html',users=user)
	container = Pelanggan.query.order_by(desc(Pelanggan.date_created))
	return render_template('admin_pelanggan.html', title='Pelanggan',container = container)

@app.route('/admin/pelanggan/add', methods=['GET','POST'])
def admin_addpel():
	if request.method == 'POST':
		reg=request.form
		noreg=reg['norek']
		nama=reg['nama']
		alamat=reg['alamat']
		kota=reg['kota']
		kec=reg['kec']
		kdpos=reg['kodepos']
		daya=reg['daya']

		print(noreg,nama,alamat,kota,kec,daya,kdpos)
		AddPel=Pelanggan(id=noreg,nama=nama,alamat=alamat,kota=kota,kec=kec,kdpos=kdpos,daya=daya)
		db.session.add(AddPel)
		db.session.commit()
		flash('Data Pelanggan Berhasil Disimpan','success')
		return redirect(url_for('admin_pelanggan'))
	return render_template('admin_addpel.html')


@app.route('/admin/pelanggan/ubah/<id>',methods=['GET','POST'])
def admin_ubahpel(id):
    UbahPel=Pelanggan.query.filter_by(id=id).first()
    if request.method == 'POST':
        UbahPel.id = request.form['id']
        UbahPel.nama = request.form['nama']
        UbahPel.alamat=request.form['alamat']
        UbahPel.kota=request.form['kota']
        UbahPel.kec=request.form['kec']
        UbahPel.daya=request.form['daya']
        db.session.add(UbahPel)
        db.session.commit()
        flash('Data Pelanggan Berhasil Diedit','success')
        return redirect(url_for('admin_pelanggan'))
    return render_template('admin_ubahpelanggan.html',pelanggan=UbahPel)

@app.route('/admin/pelanggan/hapus/<id>',methods=['GET','POST'])
def admin_hapuspel(id):
    HapusPel=Pelanggan.query.filter_by(id=id).first()
    db.session.delete(HapusPel)
    db.session.commit()
    flash('Data Pelanggan Berhasil Dihapus','success')
    return redirect(url_for('admin_pelanggan'))

@app.route('/admin/temuan', methods=['GET','POST'])
def admin_temuan():
	container = Temuan.query.order_by(desc(Temuan.date_created))
	if request.method == 'POST':
		reg=request.form
		norek=reg['norek']
		user= Temuan.query.filter_by(id=norek).first()
		print(norek)
		#flash('Data Pelanggan Berhasil Disimpan','success')
		return render_template('admin_temuan_cari.html',users=user)
	else:
		return render_template('admin_temuan.html', title='Temuan',container=container)


@app.route('/admin/temuan/hapus/<id>',methods=['GET','POST'])
def admin_hapustem(id):
	HapusTem=Temuan.query.filter_by(id=id).first()
	db.session.delete(HapusTem)
	db.session.commit()
	flash('Data Pelanggan Berhasil Dihapus','success')
	return redirect(url_for('admin_temuan'))

@app.route('/admin/temuan/lokasi/<id>', methods=['GET','POST'])
def admin_lokasitem(id):
    data=Temuan.query.filter_by(id=id).first()
    if request.method == 'POST':
        data.id = request.form['id']
        data.user_id=request.form['user_id']
        return 'paslek'
    else:
        return render_template('admin_lokasitem.html', temuan=data)

@app.route('/dashboard', methods=['GET', 'POST'])
def user():
	if 'user' not in session:
		return render_template('index.html', message="Anda Belum Login")

	DataUser = {
	'id' : escape(session['user']['id']),
	'username' : escape(session['user']['username'])
	}

	ModelsMessage = db.session.query(Temuan, Petugas).outerjoin(Petugas, Petugas.id == Temuan.user_id).order_by(asc(Temuan.id)).all()
	return render_template('dashboard.html',data_user=DataUser, messages=ModelsMessage)

@app.route('/user/dashboard', methods=['GET','POST'])
def user_dashboard():
	return ' iki halaman dashboard, untuk memasukkan data temuan'


@app.route('/petugas/home',methods=['GET','POST'])
def user_home():
    if 'user' not in session:
        return redirect(url_for('index'))

    DataUser = {
    'id' : escape(session['user']['id']),
    'username' : escape(session['user']['username'])
    }

    user_id=DataUser['id']
    user_username=DataUser['username']
    #print(user_username)

    data_user=Petugas.query.filter_by(username=user_username).first()
    return render_template('user_profile.html',title='Profile',user=data_user)

@app.route('/petugas/pelanggan', methods=['GET','POST'])
def user_pelanggan():
	#if 'user' not in session:
		#return redirect(url_for('index'))
	if request.method == 'POST':
		reg=request.form
		norek=reg['norek']
		user= Pelanggan.query.filter_by(id=norek).first()
		print(norek)
		#flash('Data Pelanggan Berhasil Disimpan','success')
		return render_template('user_pelanggan_cari.html',users=user)

	container = Pelanggan.query.order_by(desc(Pelanggan.date_created))
	return render_template('user_pelanggan.html',title='Data Pelanggan', container = container)


@app.route('/petugas/temuan', methods=['GET', 'POST'])
def user_temuan():
	if 'user' not in session:
		return redirect(url_for('index'))

	DataUser = {
	'id' : escape(session['user']['id']),
	'username' : escape(session['user']['username'])
	}
	user_id=DataUser['id']
	user_username=DataUser['username']

	if request.method == 'POST':
		reg=request.form
		norek=reg['norek']
		user= Temuan.query.filter_by(id=norek).first()
		print(norek)
		#flash('Data Pelanggan Berhasil Disimpan','success')
		return render_template('user_temuan_cari.html',users=user)


	data_temuan=Temuan.query.filter_by(petugas_id=user_id).order_by(desc(Temuan.date_created)).all()
	return render_template('user_temuan.html',container=data_temuan,title='Temuan')


@app.route('/petugas/addtemuan', methods=['GET', 'POST'])
def user_addtem():
	if 'user' not in session:
		return redirect(url_for('index'))

	DataUser = {
	'id' : escape(session['user']['id']),
	'username' : escape(session['user']['username'])
	}

	if request.method == 'POST':
		pelanggan = request.form['opts']
		ket = request.form['ket']
		lat = request.form['lat']
		lng = request.form['lng']
		print(lat,lng)
		AddTemuan=Temuan(petugas_id=DataUser['id'],pelanggan_id=pelanggan, ket=ket, lat=lat, lng=lng)
        #AddTemuan=Temuan(pelanggan_id=pelanggan,tindakan=tindakan, ket=ket)
        #AddPel=Pelanggan(lat=lat,lng=lng)
        #db.session.add(AddPel)
		db.session.add(AddTemuan)
		db.session.commit()
		flash('Data Temuan Berhasil Disimpan','success')
		return redirect(url_for('user_temuan'))
	return render_template('user_addtemuan.html', container=Pelanggan.query.all())

@app.route('/petugas/tindakan/<id>',methods=['GET','POST'])
def petugas_tindakan(id):
	getdata = Temuan.query.filter_by(id=id).first()

	if 'user' not in session:
		return redirect(url_for('index'))

	DataUser = {
	'id' : escape(session['user']['id']),
	'username' : escape(session['user']['username'])
	}

	if request.method == 'POST':
		no_tem= request.form['notem']
		nm_pet = request.form['nmpet']
		id_pel = request.form['idpel']
		status = request.form['ditangani']
		tindakan = request.form['ket']
		print(no_tem,nm_pet,id_pel,status,tindakan)
		AddTindakan=Tindakan(temuan_id=no_tem,petugas_id=nm_pet, pelanggan_id=id_pel,ket=tindakan)
		getdata.status= request.form['ditangani']
		db.session.add(getdata)
		db.session.add(AddTindakan)
		db.session.commit()
		return 'oke'
	else:
		return render_template('petugas_addtindakan.html',tem=getdata)


@app.route('/petugas/tindakan',methods=['GET','POST'])
def pet_tindakan():
	if 'user' not in session:
		return redirect(url_for('index'))

	DataUser = {
	'id' : escape(session['user']['id']),
	'username' : escape(session['user']['username'])
	}
	user_id=DataUser['id']
	user_username=DataUser['username']

	container = Tindakan.query.filter_by(petugas_id=user_id).order_by(desc(Tindakan.date_created)).all()

	if request.method == 'POST':
		cari = request.form['cari']
		data = Tindakan.query.filter_by(id=cari).first()
		print(cari)
		return 'oke yak'
	else:
		return render_template('petugas_tindakan.html', title='Tindakan', container=container)

@app.route('/petugas/tindakan/hapus/<id>',methods=['GET','POST'])
def petugas_hapustin(id):
	HapusTin=Tindakan.query.filter_by(id=id).first()
	db.session.delete(HapusTin)
	db.session.commit()
	flash('Data Pelanggan Berhasil Dihapus','success')
	return redirect(url_for('pet_tindakan'))



@app.route('/maps',methods=['GET','POST'])
def maps():
	return render_template('maps.html')

@app.route('/getsession', methods=['GET','POST'])
def getsession():
	if 'user' in session:
		return session['user']

@app.route("/logout")
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))


@app.route('/logoutuser')
def user_logout():
	session.pop('user',None)
	return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)

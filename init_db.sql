-- Table 'Usuario'
DROP TABLE IF EXISTS IntentoIncorrecto;
DROP TABLE IF EXISTS IntentoCorrecto;
DROP TABLE IF EXISTS Boleto;
DROP TABLE IF EXISTS Imagen;
DROP TABLE IF EXISTS UsuarioNormal;
DROP TABLE IF EXISTS UsuarioRed;
DROP TABLE IF EXISTS Usuario;
DROP TABLE IF EXISTS Casilla;
DROP TABLE IF EXISTS Evento;
DROP TABLE IF EXISTS Pregunta;


-- DROP TABLE IF EXISTS Usuario;
CREATE TABLE Usuario (
  idUsuario INT IDENTITY(1,1) PRIMARY KEY,
  usuario VARCHAR(50) NOT NULL,
  idEvento INT NOT NULL,
  contacto VARCHAR(100) NOT NULL -- Aquí guardamos el correo o red social
);


-- Tabla derivada: UsuarioNormal
CREATE TABLE UsuarioNormal (
  idUsuario INT PRIMARY KEY,
  contrasena VARCHAR(100) NOT NULL,
  FOREIGN KEY (idUsuario) REFERENCES Usuario(idUsuario)
);

-- Tabla derivada: UsuarioRed
CREATE TABLE UsuarioRed (
  idUsuario INT PRIMARY KEY,
  FOREIGN KEY (idUsuario) REFERENCES Usuario(idUsuario)
);

-- Table 'Boleto'
-- DROP TABLE IF EXISTS Boleto;
CREATE TABLE Boleto (
  idBoleto INT IDENTITY(1,1) PRIMARY KEY,
  tipo BIT NOT NULL,
  idUsuario INT NOT NULL
);

-- Table 'Casilla'
--DROP TABLE IF EXISTS Casilla;
-- Table 'Casilla'
CREATE TABLE Casilla (
  idCasilla INT NOT NULL,
  idImagen INT NOT NULL,
  coordenadaX INT NOT NULL,
  coordenadaY INT NOT NULL,
  idPregunta INT NOT NULL,
  estado VARCHAR(20) DEFAULT 'libre' NOT NULL,  -- 👈 Aquí la agregas
  PRIMARY KEY (idCasilla, idImagen)
);


-- Table 'Pregunta'
--DROP TABLE IF EXISTS Pregunta;
CREATE TABLE Pregunta (
  idPregunta INT IDENTITY(1,1) PRIMARY KEY,
  pregunta VARCHAR(200) NOT NULL,
  opcionA VARCHAR(50),
  opcionB VARCHAR(50),
  opcionC VARCHAR(50),
  opcionD VARCHAR(50),
  respuesta VARCHAR(7) NOT NULL
);

-- Table 'IntentoCorrecto'
--DROP TABLE IF EXISTS IntentoCorrecto;
CREATE TABLE IntentoCorrecto (
  idCorrecto INT IDENTITY(1,1) PRIMARY KEY,
  idUsuario INT NOT NULL,
  idCasilla INT NOT NULL,
  idImagen INT NOT NULL
);

-- Table 'IntentoIncorrecto'
--DROP TABLE IF EXISTS IntentoIncorrecto;
CREATE TABLE IntentoIncorrecto (
  idIncorrecto INT IDENTITY(1,1) PRIMARY KEY,
  opcionElegida VARCHAR(7) NOT NULL,
  idUsuario INT NOT NULL,
  idCasilla INT NOT NULL,
  idImagen INT NOT NULL
);

-- Table 'Evento'
--DROP TABLE IF EXISTS Evento;
CREATE TABLE Evento (
  idEvento INT IDENTITY(1,1) PRIMARY KEY,
  fechaInicio DATETIME NOT NULL,
  fechaFinal DATETIME NOT NULL
);

-- Table 'Imagen'
--DROP TABLE IF EXISTS Imagen;
CREATE TABLE Imagen (
  idImagen INT IDENTITY(1,1) PRIMARY KEY,
  URL VARCHAR(200) NOT NULL,
  estado BIT NOT NULL,
  respuesta VARCHAR(50) NOT NULL,
  idEvento INT NOT NULL,
  idUsuario INT
);

-- Foreign Keys
ALTER TABLE Usuario ADD FOREIGN KEY (idEvento) REFERENCES Evento (idEvento);
ALTER TABLE Boleto ADD FOREIGN KEY (idUsuario) REFERENCES Usuario (idUsuario);
ALTER TABLE Casilla ADD FOREIGN KEY (idPregunta) REFERENCES Pregunta (idPregunta);
ALTER TABLE IntentoCorrecto ADD FOREIGN KEY (idUsuario) REFERENCES Usuario (idUsuario);
ALTER TABLE IntentoCorrecto ADD FOREIGN KEY (idCasilla, idImagen) REFERENCES Casilla (idCasilla, idImagen);
-- ALTER TABLE IntentoCorrecto ADD FOREIGN KEY (idImagen) REFERENCES Imagen (idImagen);
ALTER TABLE IntentoIncorrecto ADD FOREIGN KEY (idUsuario) REFERENCES Usuario (idUsuario);
ALTER TABLE IntentoIncorrecto ADD FOREIGN KEY (idCasilla, idImagen) REFERENCES Casilla (idCasilla, idImagen);
-- ALTER TABLE IntentoIncorrecto ADD FOREIGN KEY (idImagen) REFERENCES Imagen (idImagen);
ALTER TABLE Imagen ADD FOREIGN KEY (idEvento) REFERENCES Evento (idEvento);
ALTER TABLE Imagen ADD FOREIGN KEY (idUsuario) REFERENCES Usuario (idUsuario);


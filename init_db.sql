-- Table 'Usuario'
DROP TABLE IF EXISTS IntentoIncorrecto;
DROP TABLE IF EXISTS IntentoCorrecto;
DROP TABLE IF EXISTS Boleto;
DROP TABLE IF EXISTS Imagen;
DROP TABLE IF EXISTS Usuario;
DROP TABLE IF EXISTS Casilla;
DROP TABLE IF EXISTS Evento;
DROP TABLE IF EXISTS Pregunta;


-- DROP TABLE IF EXISTS Usuario;
CREATE TABLE Usuario (
  idUsuario INT IDENTITY(1,1) PRIMARY KEY,
  usuario VARCHAR(50) NOT NULL,
  idEvento INT NOT NULL
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
CREATE TABLE Casilla (
  idCasilla INT NOT NULL,
  idImagen INT NOT NULL,
  coordenadaX INT NOT NULL,
  coordenadaY INT NOT NULL,
  casilla BIT NOT NULL,
  idPregunta INT NOT NULL,
  PRIMARY KEY (idCasilla, idImagen) -- Clave primaria compuesta
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


--Datos dummy
INSERT INTO Evento (fechaInicio, fechaFinal) VALUES
('2006-05-08 03:05:15', '2006-05-08 03:05:15');

INSERT INTO Imagen (URL, estado, respuesta, idEvento, idUsuario) VALUES
('jsfhsrhfkjdhfkjhdkj', 0, 'jshfu', 1, NULL);

INSERT INTO Usuario (usuario, idEvento) VALUES
('valeria', 1);

INSERT INTO Boleto (tipo, idUsuario) VALUES
(0, 1);

INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES
('hola', 'e', 'r', 'v', 's', 'opcionA');

INSERT INTO Casilla (idCasilla, idImagen, coordenadaX, coordenadaY, estado, idPregunta) VALUES
(1, 1, 23, 43,0, 1);

INSERT INTO IntentoCorrecto (idUsuario, idCasilla, idImagen) VALUES
(1, 1, 1);

INSERT INTO IntentoIncorrecto (opcionElegida, idUsuario, idCasilla, idImagen) VALUES
('opcionB', 1, 1, 1);


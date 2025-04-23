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

INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Quién dirigió la película Titanic (1997)?', 'Steven Spielberg', 'James Cameron', 'Martin Scorsese', 'Ridley Scott', 'opcionRespuesta: b')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué película ganó el Óscar a Mejor Película en 1994?', 'Forrest Gump', 'Pulp Fiction', 'The Shawshank Redemption', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: d) La lista de Schindler', '', '¿Quién interpretó a Joker en The Dark Knight (2008)?', 'Jared Leto', 'Joaquin Phoenix', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Jack Nicholson', 'Heath Ledger', '', '¿En qué año se estrenó El Padrino?', '1969', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) 1975', '1980', '1972', '', '¿Qué director es conocido por la trilogía El Señor de los Anillos?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Christopher Nolan', 'Peter Jackson', 'David Fincher', 'Peter Jackson', '', 'opcion¿Qué actor protagonizó Misión Imposible como Ethan Hunt?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Matt Damon', 'Tom Cruise', 'Bruce Willis', 'Keanu Reeves', 'Tom Cruise', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Cómo se llama el planeta natal de los Na’vi en Avatar?', 'Pandora', 'Narnia', 'Krypton', 'Arrakis', 'opcionRespuesta: a')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué película es famosa por la frase “May the Force be with you”?', 'Star Trek', 'Guardians of the Galaxy', 'Star Wars', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: c) Star Wars', '', '¿Qué actriz ganó un Óscar por su papel en La La Land?', 'Emma Stone', 'Jennifer Lawrence', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Anne Hathaway', 'Emma Stone', '', '¿Qué película animada de Pixar cuenta la historia de una rata cocinera?', 'Ratatouille', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Wall-E', 'Inside Out', 'Ratatouille', '', '¿Quién interpretó a Iron Man en el Universo Cinematográfico de Marvel?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Chris Evans', 'Robert Downey Jr.', 'Mark Ruffalo', 'Robert Downey Jr.', '', 'opcion¿En qué película aparece el personaje de Hannibal Lecter?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Psycho', 'El silencio de los inocentes', 'American Psycho', 'Seven', 'El silencio de los inocentes', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué película tiene el récord de más premios Óscar ganados?', 'Ben-Hur', 'Titanic', 'El Señor de los Anillos: El retorno del Rey', 'Todas las anteriores', 'opcionRespuesta: d')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué actriz interpretó a Katniss Everdeen en Los Juegos del Hambre?', 'Emma Watson', 'Shailene Woodley', 'Jennifer Lawrence', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: c) Jennifer Lawrence', '', '¿Qué película de terror fue dirigida por Jordan Peele en 2017?', 'Us', 'Hereditary', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Get Out', 'Get Out', '', '¿Qué película animada trata sobre un niño que entra al mundo de los muertos?', 'The Book of Life', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Encanto', 'Soul', 'Coco', '', '¿Qué actor protagonizó John Wick?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Keanu Reeves', 'Liam Neeson', 'Vin Diesel', 'Keanu Reeves', '', 'opcion¿Qué película fue el debut como director de Quentin Tarantino?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Pulp Fiction', 'Jackie Brown', 'Reservoir Dogs', 'Kill Bill', 'Reservoir Dogs', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué película se basa en la vida de Stephen Hawking?', 'The Imitation Game', 'The Theory of Everything', 'A Beautiful Mind', 'Interstellar', 'opcionRespuesta: b')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Quién interpreta a Jack Sparrow en Piratas del Caribe?', 'Orlando Bloom', 'Johnny Depp', 'Tom Hanks', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: b) Johnny Depp', '', '¿Qué película popularizó el uso del “bullet time”?', 'Inception', 'The Matrix', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Equilibrium', 'The Matrix', '', '¿Cuál es el nombre del protagonista en El Rey León?', 'Simba', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Scar', 'Mufasa', 'Simba', '', '¿Qué película de 2023 ganó el Óscar a Mejor Película?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Everything Everywhere All at Once', 'The Fabelmans', 'TÁR', 'Everything Everywhere All at Once', '', 'opcion¿Qué director es famoso por películas como Inception y Interstellar?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) David Fincher', 'James Cameron', 'Christopher Nolan', 'Wes Anderson', 'Christopher Nolan', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué actor ganó un Óscar por The Revenant?', 'Brad Pitt', 'Leonardo DiCaprio', 'Tom Hardy', 'Matt Damon', 'opcionRespuesta: b')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué musical fue protagonizado por Hugh Jackman como P.T. Barnum?', 'Les Misérables', 'Chicago', 'The Greatest Showman', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: c) The Greatest Showman', '', '¿Qué película animada de Disney se desarrolla en Colombia?', 'Luca', 'Encanto', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Raya', 'Encanto', '', '¿Quién dirigió Psicosis (1960)?', 'Stanley Kubrick', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Billy Wilder', 'Orson Welles', 'Alfred Hitchcock', '', '¿En qué saga aparece el personaje Gollum?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Star Wars', 'El Señor de los Anillos', 'Crónicas de Narnia', 'El Señor de los Anillos', '', 'opcion¿Qué actriz interpretó a Hermione Granger?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Emma Stone', 'Emma Watson', 'Natalie Portman', 'Dakota Fanning', 'Emma Watson', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Quién dirigió Roma (2018)?', 'Guillermo del Toro', 'Alfonso Cuarón', 'Alejandro G. Iñárritu', 'Pedro Almodóvar', 'opcionRespuesta: b')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué película tiene a un tiburón blanco como antagonista?', 'Piraña', 'Deep Blue Sea', 'Jaws', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: c) Jaws', '', '¿Qué película trata de una invasión alienígena en el Día de la Independencia de EE.UU.?', 'War of the Worlds', 'Independence Day', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Battleship', 'Independence Day', '', '¿Quién interpreta a Deadpool?', 'Chris Pratt', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Chris Pine', 'Tom Holland', 'Ryan Reynolds', '', '¿Cuál es el nombre del personaje principal en Gladiador?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Commodus', 'Marcus', 'Lucius', 'Maximus', '', 'opcion¿Qué película protagonizó Julia Roberts como prostituta?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Notting Hill', 'My Best Friend's Wedding', 'Pretty Woman', 'Erin Brockovich', 'Pretty Woman', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué película ganó el Óscar a Mejor Película en 2020?', 'Joker', '1917', 'Parasite', 'Once Upon a Time in Hollywood', 'opcionRespuesta: c')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué director es conocido por La forma del agua y El laberinto del fauno?', 'Alfonso Cuarón', 'Guillermo del Toro', 'Tim Burton', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: b) Guillermo del Toro', '', '¿Qué saga protagoniza Tom Holland como un superhéroe?', 'Batman', 'Superman', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) X-Men', 'Spider-Man', '', '¿Qué película popularizó la canción “My Heart Will Go On”?', 'Moulin Rouge', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Titanic', 'Romeo + Juliet', 'Titanic', '', '¿Qué personaje dice la frase “Here’s Johnny!”?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Freddy Krueger', 'Jack Torrance', 'Michael Myers', 'Jack Torrance', '', 'opcion¿Qué película cuenta la historia de un náufrago con un balón llamado Wilson?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Life of Pi', 'Cast Away', 'The Beach', 'Captain Phillips', 'Cast Away', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué película se centra en una inteligencia artificial llamada HAL 9000?', 'Ex Machina', 'Blade Runner', '2001: A Space Odyssey', 'I, Robot', 'opcionRespuesta: c')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué película infantil tiene personajes llamados Mike y Sulley?', 'Toy Story', 'Monsters Inc.', 'Finding Nemo', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: b) Monsters Inc.', '', '¿Qué actriz protagonizó Black Swan?', 'Mila Kunis', 'Anne Hathaway', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Rooney Mara', 'Natalie Portman', '', '¿Qué película protagoniza Benedict Cumberbatch como Alan Turing?', 'The Theory of Everything', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) The Imitation Game', 'Enigma', 'The Imitation Game', '', '¿Qué película de 2014 muestra un viaje en el espacio y agujeros de gusano?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Ad Astra', 'Interstellar', 'The Martian', 'Interstellar', '', 'opcion¿Qué personaje de Disney canta “Let It Go”?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Moana', 'Elsa', 'Anna', 'Rapunzel', 'Elsa', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué actor protagonizó El Renacido?', 'Brad Pitt', 'Christian Bale', 'Leonardo DiCaprio', 'Tom Hardy', 'opcionRespuesta: c')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué película de 1999 trata sobre un chico que ve fantasmas?', 'Poltergeist', 'The Others', 'The Sixth Sense', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: c) The Sixth Sense', '', '¿Cuál es el nombre del fontanero protagonista de muchos juegos de Nintendo?', 'Luigi', 'Mario', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Yoshi', 'Mario', '', '¿Qué empresa desarrolló The Legend of Zelda?', 'Sony', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Nintendo', 'Sega', 'Nintendo', '', '¿En qué videojuego aparece el personaje Master Chief?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Halo', 'Destiny', 'Doom', 'Halo', '', 'opcion¿Qué juego popularizó el género battle royale?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Call of Duty: Warzone', 'Fortnite', 'PUBG', 'Apex Legends', 'PUBG', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué videojuego tiene como objetivo principal construir con bloques?', 'Silent Hill 4', 'Roblox', 'Minecraft', 'Sims', 'opcionRespuesta: c')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿En qué consola debutó el juego God of War?', 'Xbox', 'PlayStation 2', 'GameCube', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: b) PlayStation 2', '', '¿Cómo se llama el personaje principal de la saga The Witcher?', 'Altair', 'Geralt', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Kratos', 'Geralt', '', '¿Qué juego de Rockstar Games presenta a tres protagonistas?', 'GTA IV', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Red Dead Redemption', 'L.A. Noire', 'GTA V', '', '¿Cuál es el nombre del primer Pokémon que aparece en la Pokédex nacional?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Bulbasaur', 'Charmander', 'Squirtle', 'Bulbasaur', '', 'opcion¿Qué videojuego de 1980 es famoso por su personaje amarillo que come puntos?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Donkey Kong', 'Tetris', 'Pac-Man', 'Frogger', 'Pac-Man', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Cuál es el principal enemigo en la saga Resident Evil?', 'Umbrella Corporation', 'Hydra', 'Tricell', 'Cerberus', 'opcionRespuesta: a')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué personaje es el rival de Sonic the Hedgehog?', 'Metal Sonic', 'Dr. Eggman', 'Shadow', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: b) Dr. Eggman', '', '¿Cuál es el nombre de la princesa que Mario suele rescatar?', 'Zelda', 'Peach', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Rosalina', 'Peach', '', '¿Qué juego fue creado por Hideo Kojima y es conocido por su sigilo?', 'Assassin’s Creed', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Splinter Cell', 'Hitman', 'Metal Gear Solid', '', '¿Cuál es el protagonista de The Last of Us?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) John', 'Ethan', 'Jack', 'Joel', '', 'opcion¿En qué juego puedes explorar Hyrule?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Dark Souls', 'The Legend of Zelda', 'Skyrim', 'Final Fantasy', 'The Legend of Zelda', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué videojuego fue un éxito de ventas para Wii y usaba controles de movimiento?', 'Wii Sports', 'Super Smash Bros.', 'Zelda: Twilight Princess', 'Mario Galaxy', 'opcionRespuesta: a')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué tipo de juego es League of Legends?', 'MOBA', 'FPS', 'RPG', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: a) MOBA', '', '¿En qué país fue creado Tetris?', 'EE.UU.', 'Japón', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Alemania', 'Rusia', '', '¿Qué arma es característica en DOOM?', 'BFG 9000', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Plasma Sword', 'Gravity Gun', 'BFG 9000', '', '¿En qué videojuego manejas a un asesino con una hoja oculta?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Dishonored', 'Hitman', 'Prince of Persia', 'Assassin’s Creed', '', 'opcion¿Qué criatura es icónica en Monster Hunter?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Rathalos', 'Chocobo', 'Behemoth', 'Leviathan', 'Rathalos', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué título es un simulador de vida desarrollado por Maxis?', 'Animal Crossing', 'The Sims', 'Stardew Valley', 'Second Life', 'opcionRespuesta: b')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué empresa es creadora de Overwatch?', 'EA', 'Riot Games', 'Blizzard', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: c) Blizzard', '', '¿Cuál es el nombre del mundo en Dark Souls?', 'Lordran', 'Hyrule', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Midgard', 'Lordran', '', '¿Qué personaje de Nintendo es conocido por aspirar enemigos?', 'Yoshi', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Pikachu', 'Link', 'Kirby', '', '¿Qué videojuego se ambienta en un mundo postapocalíptico lleno de zombis con parkour?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Fallout', 'Days Gone', 'Dying Light', 'Dying Light', '', 'opcion¿Qué consola fue lanzada por Sony en 2020?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) PlayStation 4', 'PlayStation 5', 'PSP', 'PS Vita', 'PlayStation 5', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué videojuego es conocido por la frase “War. War never changes”?', 'Call of Duty', 'Medal of Honor', 'Fallout', 'Gears of War', 'opcionRespuesta: c')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Cuál fue la primera consola portátil de Nintendo?', 'DS', 'Game Boy', 'Switch', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: b) Game Boy', '', '¿Qué videojuego protagoniza el personaje llamado Arthur Morgan?', 'GTA V', 'Mafia III', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Far Cry 5', 'Red Dead Redemption II', '', '¿Qué personaje aparece en Street Fighter?', 'Liu Kang', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Scorpion', 'Jin', 'Ryu', '', '¿Qué criatura cuida los templos en Shadow of the Colossus?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Titanes', 'Colosos', 'Dragones', 'Colosos', '', 'opcion¿Qué significa MMORPG?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Massive Online Game', 'Multi Online World', 'Massively Multiplayer Online Role-Playing Game', 'Mobile Online RPG', 'Massively Multiplayer Online Role-Playing Game', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué protagonista tiene un brazo mecánico en Sekiro?', 'The Wolf', 'Shinobi', 'Jin Sakai', 'Kensei', 'opcionRespuesta: a')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿En qué juego puedes usar el "Fus Ro Dah"?', 'Oblivion', 'Skyrim', 'Elden Ring', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: b) Skyrim', '', '¿Qué consola fue lanzada por Microsoft en 2001?', 'Xbox', 'Xbox 360', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Dreamcast', 'Xbox', '', '¿Qué criatura es común en los juegos de Pokémon?', 'Goomba', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Pikachu', 'Slime', 'Pikachu', '', '¿En qué juego aparece el personaje Kratos?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Darksiders', 'God of War', 'Castlevania', 'God of War', '', 'opcion¿Qué desarrolladora creó Half-Life?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Valve', 'Ubisoft', 'id Software', 'Activision', 'Valve', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué juego combina construcción, supervivencia y minería?', 'Halo', 'Raft', 'Cult of The Lamb', 'Minecraft', 'opcionRespuesta: d')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué color representa al personaje principal de Among Us más comúnmente?', 'Verde', 'Rojo', 'Azul', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: b) Rojo', '', '¿Qué videojuego se desarrolla en Rapture?', 'BioShock', 'Dishonored', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Subnautica', 'BioShock', '', '¿Qué protagonista puede detener el tiempo en Life is Strange?', 'Max', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Kate', 'Rachel', 'Max', '', '¿Qué videojuego fue pionero del género survival horror en 1996?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Silent Hill', 'Alone in the Dark', 'Dino Crisis', 'Resident Evil', '', 'opcion¿Qué juego tiene lugar en la isla de Yara?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Far Cry 6', 'Just Cause 4', 'Uncharted 4', 'Assassin’s Creed IV', 'Far Cry 6', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué personaje usa un escudo con forma de estrella?', 'Iron Man', 'Captain America', 'Black Panther', 'Spider-Man', 'opcionRespuesta: b')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué juego mezcla elementos de shooter y construcción?', 'Apex Legends', 'PUBG', 'Fortnite', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: c) Fortnite', '', '¿Qué desarrolladora es responsable de The Elder Scrolls y Fallout?', 'CD Projekt', 'BioWare', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Obsidian', 'Bethesda', '', '¿Qué juego indie populariza la agricultura y relaciones sociales?', 'Stardew Valley', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Slime Rancher', 'Harvest Moon', 'Stardew Valley', '', '¿Cuál es el río más largo del mundo?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Nilo', 'Yangtsé', 'Misisipi', 'Nilo', '', 'opcion¿En qué año llegó el hombre a la Luna por primera vez?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) 1965', '1969', '1971', '1973', '1969', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Cuál es el país más grande del mundo por superficie?', 'Canadá', 'China', 'Estados Unidos', 'Rusia', 'opcionRespuesta: d')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Quién pintó la obra "La última cena"?', 'Miguel Ángel', 'Rafael', 'Leonardo da Vinci', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: c) Leonardo da Vinci', '', '¿Cuál es el océano más grande del planeta?', 'Atlántico', 'Índico', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Ártico', 'Pacífico', '', '¿Qué país tiene la mayor población del mundo?', 'India', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) China', 'Indonesia', 'India', '', '¿Cuál es la capital de Australia?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Melbourne', 'Canberra', 'Brisbane', 'Canberra', '', 'opcion¿En qué continente se encuentra el desierto del Sahara?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Asia', 'África', 'América', 'Oceanía', 'África', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué instrumento mide la intensidad de los terremotos?', 'Barómetro', 'Sismógrafo', 'Anemómetro', 'Termómetro', 'opcionRespuesta: b')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Cuál es el metal más ligero?', 'Oro', 'Aluminio', 'Litio', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: c) Litio', '', '¿Quién escribió "La Odisea"?', 'Sófocles', 'Homero', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Aristófanes', 'Homero', '', '¿Cuál es el planeta más cercano al Sol?', 'Venus', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Mercurio', 'Marte', 'Mercurio', '', '¿Qué gas es esencial para la respiración humana?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Nitrógeno', 'Oxígeno', 'Hidrógeno', 'Oxígeno', '', 'opcion¿En qué país se encuentra la Torre Eiffel?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Italia', 'Francia', 'Alemania', 'España', 'Francia', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Cuál es la moneda oficial de Japón?', 'Yuan', 'Yen', 'Won', 'Dólar', 'opcionRespuesta: b')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Quién fue el primer presidente de Estados Unidos?', 'Thomas Jefferson', 'George Washington', 'Abraham Lincoln', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: b) George Washington', '', '¿Cuál es el idioma más hablado en el mundo?', 'Inglés', 'Español', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Árabe', 'Inglés', '', '¿Qué país es conocido por la samba y el carnaval de Río?', 'Argentina', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Brasil', 'Colombia', 'Brasil', '', '¿Qué científico propuso la teoría de la relatividad?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Albert Einstein', 'Galileo Galilei', 'Nikola Tesla', 'Albert Einstein', '', 'opcion¿Cuál es el continente con más países?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Asia', 'África', 'Europa', 'América', 'África', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué elemento químico tiene el símbolo "O"?', 'Oro', 'Oxígeno', 'Osmio', 'Oxalato', 'opcionRespuesta: b')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Cuál es la capital de Canadá?', 'Toronto', 'Vancouver', 'Ottawa', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: c) Ottawa', '', '¿En qué año comenzó la Segunda Guerra Mundial?', '1935', '1939', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) 1945', '1939', '', '¿Qué país es famoso por las pirámides de Giza?', 'México', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Perú', 'India', 'Egipto', '', '¿Cuál es el animal terrestre más rápido?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Tigre', 'Guepardo', 'Antílope', 'Guepardo', '', 'opcion¿Qué órgano del cuerpo humano bombea la sangre?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Pulmón', 'Hígado', 'Corazón', 'Riñón', 'Corazón', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Cuál es el país más pequeño del mundo?', 'Mónaco', 'San Marino', 'Nauru', 'Ciudad del Vaticano', 'opcionRespuesta: d')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué instrumento musical tiene teclas blancas y negras?', 'Violín', 'Guitarra', 'Piano', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: c) Piano', '', '¿En qué país se originaron los Juegos Olímpicos?', 'Italia', 'Grecia', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Alemania', 'Grecia', '', '¿Cuál es el símbolo químico del oro?', 'Au', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Fe', 'Pb', 'Au', '', '¿Qué continente no tiene desiertos?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Asia', 'América', 'Oceanía', 'Europa', '', 'opcion¿Cuál es la capital de Suiza?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Zürich', 'Ginebra', 'Berna', 'Lucerna', 'Berna', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué inventor es conocido por crear la bombilla eléctrica?', 'Nikola Tesla', 'Thomas Edison', 'Benjamin Franklin', 'Alexander Graham Bell', 'opcionRespuesta: b')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿En qué país está el monte Everest?', 'China', 'Nepal', 'India', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: b) Nepal', '', '¿Cuál es el idioma oficial de Brasil?', 'Español', 'Portugués', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Francés', 'Portugués', '', '¿Cuántos corazones tiene un pulpo?', 'Uno', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Tres', 'Cuatro', 'Tres', '', '¿Cuál es el país con más islas del mundo?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Indonesia', 'Noruega', 'Suecia', 'Suecia', '', 'opcion¿Qué famoso explorador descubrió América en 1492?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Fernando de Magallanes', 'Cristóbal Colón', 'Vasco da Gama', 'Hernán Cortés', 'Cristóbal Colón', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Cuál es la unidad de medida de la energía?', 'Newton', 'Joule', 'Pascal', 'Watt', 'opcionRespuesta: b')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿En qué continente está Argentina?', 'Europa', 'Asia', 'América', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: c) América', '', '¿Cuál es el mayor depósito de agua dulce del planeta?', 'Lago Victoria', 'Lago Titicaca', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Lago Baikal', 'Lago Baikal', '', '¿Cuál es el nombre de la galaxia donde está la Tierra?', 'Andrómeda', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Vía Láctea', 'Ojo Negro', 'Vía Láctea', '', '¿Cuál es el animal nacional de China?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Panda gigante', 'Dragón', 'Lobo gris', 'Panda gigante', '', 'opcion¿Cuál es el hueso más largo del cuerpo humano?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Húmerus', 'Tibiá', 'Fémur', 'Radio', 'Fémur', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Cuál es la capital de Turquía?', 'Estambul', 'Ankara', 'Esmirna', 'Bursa', 'opcionRespuesta: b')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Quién fue el autor de "El contrato social"?', 'Montesquieu', 'Voltaire', 'Rousseau', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: c) Rousseau', '', '¿Cuántos colores tiene el arcoíris?', '6', '7', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) 9', '7', '', '¿Cuál es el único planeta que gira en sentido horario?', 'Marte', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Venus', 'Neptuno', 'Venus', '', '¿Qué tipo de animal es la ballena?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Reptil', 'Anfibio', 'Mamífero', 'Mamífero', '', 'opcion¿Qué país tiene una bandera con una hoja de arce?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Australia', 'Canadá', 'Alemania', 'Reino Unido', 'Canadá', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Quién escribió Cien años de soledad?', 'Mario Vargas Llosa', 'Gabriel García Márquez', 'Pablo Neruda', 'Julio Cortázar', 'opcionRespuesta: b')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Cuál es la obra más famosa de Miguel de Cervantes?', 'La Celestina', 'Don Juan Tenorio', 'Don Quijote de la Mancha', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: c) Don Quijote de la Mancha', '', '¿Quién es el autor de 1984?', 'Aldous Huxley', 'Ray Bradbury', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Philip K. Dick', 'George Orwell', '', '¿Qué autor escribió Romeo y Julieta?', 'Christopher Marlowe', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Oscar Wilde', 'Charles Dickens', 'William Shakespeare', '', '¿En qué novela aparece el personaje de Jay Gatsby?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) El gran Gatsby', 'Rebelión en la granja', 'El guardián entre el centeno', 'El gran Gatsby', '', 'opcion¿Cuál es la nacionalidad de Franz Kafka?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Alemana', 'Austriaca', 'Checa', 'Húngara', 'Checa', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué autor escribió Crimen y castigo?', 'León Tolstói', 'Fiódor Dostoyevski', 'Antón Chéjov', 'Nikolái Gógol', 'opcionRespuesta: b')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué personaje creó Arthur Conan Doyle?', 'Hercule Poirot', 'Sherlock Holmes', 'Sam Spade', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: b) Sherlock Holmes', '', '¿Qué novela comienza con la frase “Todas las familias felices se parecen entre sí…”?', 'Madame Bovary', 'Crimen y castigo', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Orgullo y prejuicio', 'Anna Karénina', '', '¿Quién escribió Rayuela?', 'Jorge Luis Borges', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Julio Cortázar', 'Pablo Neruda', 'Julio Cortázar', '', '¿Cuál es el seudónimo de Mary Ann Evans?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) George Eliot', 'Emily Brontë', 'Jane Austen', 'George Eliot', '', 'opcion¿En qué novela aparece el personaje Holden Caulfield?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) El guardián entre el centeno', 'Los miserables', 'El retrato de Dorian Gray', 'La náusea', 'El guardián entre el centeno', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué obra fue escrita por Dante Alighieri?', 'El paraíso perdido', 'La Ilíada', 'La Divina Comedia', 'Las mil y una noches', 'opcionRespuesta: c')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Cuál de estos autores ganó el Premio Nobel de Literatura?', 'Jorge Luis Borges', 'Haruki Murakami', 'Gabriel García Márquez', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: c) Gabriel García Márquez', '', '¿Quién escribió Fahrenheit 451?', 'Isaac Asimov', 'Ray Bradbury', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Aldous Huxley', 'Ray Bradbury', '', '¿Qué poeta escribió Veinte poemas de amor y una canción desesperada?', 'César Vallejo', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Pablo Neruda', 'Octavio Paz', 'Pablo Neruda', '', '¿Quién escribió El Principito?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Antoine de Saint-Exupéry', 'Hans Christian Andersen', 'Roald Dahl', 'Antoine de Saint-Exupéry', '', 'opcion¿Cuál de estos autores es considerado parte del Boom Latinoamericano?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Mario Vargas Llosa', 'Isabel Allende', 'Octavio Paz', 'Jorge Luis Borges', 'Mario Vargas Llosa', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Quién escribió Los miserables?', 'Gustave Flaubert', 'Víctor Hugo', 'Émile Zola', 'Charles Dickens', 'opcionRespuesta: b')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué novela fue escrita por Mary Shelley?', 'Frankenstein', 'Drácula', 'El retrato de Dorian Gray', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: a) Frankenstein', '', '¿Qué libro tiene como personaje principal a Gregor Samsa?', 'La náusea', 'La metamorfosis', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) El extranjero', 'La metamorfosis', '', '¿Cuál de estas obras pertenece a la literatura griega clásica?', 'La Ilíada', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) La Divina Comedia', 'Hamlet', 'La Ilíada', '', '¿Quién escribió Ulises, obra compleja de la literatura moderna?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) James Joyce', 'T. S. Eliot', 'Samuel Beckett', 'James Joyce', '', 'opcion¿Qué novela trata sobre un joven náufrago con un tigre en un bote?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) La isla misteriosa', 'Vida de Pi', 'Robinson Crusoe', 'El viejo y el mar', 'Vida de Pi', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Quién escribió En busca del tiempo perdido?', 'Marcel Proust', 'Thomas Mann', 'Virginia Woolf', 'Italo Calvino', 'opcionRespuesta: a')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué autor escribió Ensayo sobre la ceguera?', 'Paulo Coelho', 'José Saramago', 'Gabriel García Márquez', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: b) José Saramago', '', '¿Qué novela fue escrita por Jane Austen?', 'Cumbres borrascosas', 'Jane Eyre', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) Middlemarch', 'Orgullo y prejuicio', '', '¿Qué poeta escribió Altazor?', 'Vicente Huidobro', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Rubén Darío', 'César Vallejo', 'Vicente Huidobro', '', '¿Quién escribió El perfume?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Umberto Eco', 'Milan Kundera', 'Günter Grass', 'Patrick Süskind', '', 'opcion¿Qué obra fue escrita por Homero?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) El cantar del mío Cid', 'La Odisea', 'La Eneida', 'La Divina Comedia', 'La Odisea', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué personaje aparece en Matar a un ruiseñor?', 'Holden Caulfield', 'Atticus Finch', 'Humbert Humbert', 'Tom Sawyer', 'opcionRespuesta: b')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Quién escribió Pedro Páramo?', 'Carlos Fuentes', 'Octavio Paz', 'Juan Rulfo', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: c) Juan Rulfo', '', '¿Qué libro tiene como personaje a Winston Smith?', 'Fahrenheit 451', '1984', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) La naranja mecánica', '1984', '', '¿Qué autor escribió El Aleph?', 'Julio Cortázar', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Pablo Neruda', 'Gabriel García Márquez', 'Jorge Luis Borges', '', '¿Qué novela fue escrita por Emily Brontë?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Cumbres borrascosas', 'Middlemarch', 'La inquilina de Wildfell Hall', 'Cumbres borrascosas', '', 'opcion¿Qué obra fue escrita por Goethe?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Werther', 'Crimen y castigo', 'La cartuja de Parma', 'El rojo y el negro', 'Werther', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Quién escribió La tregua?', 'Eduardo Galeano', 'Mario Benedetti', 'Julio Cortázar', 'Gabriel García Márquez', 'opcionRespuesta: b')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué autor mexicano escribió Aura?', 'Octavio Paz', 'Carlos Fuentes', 'Juan Rulfo', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: b) Carlos Fuentes', '', '¿Qué novela fue escrita por Albert Camus?', 'La náusea', 'El extranjero', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) El lobo estepario', 'El extranjero', '', '¿Qué autor es conocido por su obra La insoportable levedad del ser?', 'Milan Kundera', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Haruki Murakami', 'Orhan Pamuk', 'Milan Kundera', '', '¿Qué autor escribió Los juegos del hambre?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Suzanne Collins', 'J.K. Rowling', 'Cassandra Clare', 'Suzanne Collins', '', 'opcion¿Qué novela juvenil fue escrita por J.D. Salinger?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Las ventajas de ser invisible', 'El guardián entre el centeno', 'El dador de recuerdos', 'La lección de August', 'El guardián entre el centeno', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué poeta escribió Los heraldos negros?', 'César Vallejo', 'Vicente Huidobro', 'Rubén Darío', 'Pablo Neruda', 'opcionRespuesta: a')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué libro comienza con la frase “Llamadme Ismael”?', 'Moby-Dick', 'Robinson Crusoe', 'Drácula', 'opciond')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('Respuesta: a) Moby-Dick', '', '¿Qué obra narra la historia de Gregorio Samsa, que se convierte en insecto?', 'El proceso', 'La metamorfosis', 'opcionc')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('d) El extranjero', 'La metamorfosis', '', '¿Qué autor escribió La colmena?', 'Camilo José Cela', 'opcionb')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('c) Rafael Alberti', 'Antonio Machado', 'Camilo José Cela', '', '¿Qué novela inspiró la saga El Señor de los Anillos?', 'opciona')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('b) Beowulf', 'La Ilíada', 'El Silmarillion', 'El Hobbit', '', 'opcion¿Qué autor escribió El amor en los tiempos del cólera?')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('a) Carlos Fuentes', 'Gabriel García Márquez', 'Jorge Luis Borges', 'Isabel Allende', 'Gabriel García Márquez', 'opcion')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('¿Qué escritor creó el personaje de Tom Sawyer?', 'Mark Twain', 'Charles Dickens', 'Nathaniel Hawthorne', 'Louisa May Alcott', 'opcionRespuesta: a')
INSERT INTO Pregunta (pregunta, opcionA, opcionB, opcionC, opcionD, respuesta) VALUES ('', '¿Qué autor escribió 1984 y Rebelión en la granja?', 'Ray Bradbury', 'Aldous Huxley', 'George Orwell', 'opciond')

INSERT INTO Casilla (idCasilla, idImagen, coordenadaX, coordenadaY, idPregunta) VALUES
(1, 1, 23, 43, 1);

INSERT INTO IntentoCorrecto (idUsuario, idCasilla, idImagen) VALUES
(1, 1, 1);

INSERT INTO IntentoIncorrecto (opcionElegida, idUsuario, idCasilla, idImagen) VALUES
('opcionB', 1, 1, 1);


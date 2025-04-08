BEGIN;
--
-- Create model Diente
--
CREATE TABLE "clinica_diente" (
"id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
"codigo" varchar(7) NOT NULL UNIQUE, 
"display" varchar(100) NOT NULL, 
"definicion" varchar(100) NOT NULL);

--
-- Create model Paciente
--
CREATE TABLE "clinica_paciente" (
"id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
"activo" bool NOT NULL, 
"nombre" varchar(100) NOT NULL, 
"apellido" varchar(100) NOT NULL, 
"genero" varchar(10) NOT NULL, 
"fecha_nacimiento" date NOT NULL, 
"telefono" varchar(15) NOT NULL);      
--
-- Create model Practicante
--
CREATE TABLE "clinica_practicante" (
"id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
"activo" bool NOT NULL, 
"tratamiento" varchar(10) NOT NULL, 
"nombre" varchar(100) NOT NULL, 
"apellido" varchar(100) NOT NULL, 
"cualificacion" varchar(100) NOT NULL);
--
-- Create model Procedimiento
--
CREATE TABLE "clinica_procedimiento" (
"id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
"codigo" varchar(10) NOT NULL UNIQUE, 
"descripcion" varchar(100) NOT NULL, 
"realizado_el" date NOT NULL, 
"diente_id" bigint NOT NULL REFERENCES "clinica_diente" ("id") DEFERRABLE INITIALLY DEFERRED, 
"paciente_id" bigint NOT NULL REFERENCES "clinica_paciente" ("id") DEFERRABLE INITIALLY DEFERRED, 
"practicante_id" bigint NOT NULL REFERENCES "clinica_practicante" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE INDEX "clinica_procedimiento_diente_id_fd4389c2" ON "clinica_procedimiento" ("diente_id");
CREATE INDEX "clinica_procedimiento_paciente_id_b2a10bea" ON "clinica_procedimiento" ("paciente_id");
CREATE INDEX "clinica_procedimiento_practicante_id_060c88d6" ON "clinica_procedimiento" ("practicante_id");

COMMIT;
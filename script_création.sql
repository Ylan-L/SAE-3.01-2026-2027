-- =====================================================================
-- SAÉ 3.01 « Climat & Cultures » — Pôle DATA — Jalon 2
-- Script de création : schéma en étoile (4 dimensions + 1 table de faits)
-- SGBD : MariaDB (AlwaysData, base bddsae_agri). Rejouable : DROP puis CREATE.
-- Granularité de la table de faits : commune × culture × horizon × modèle
-- =====================================================================

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS fact_indicateur;
DROP TABLE IF EXISTS dim_commune;
DROP TABLE IF EXISTS dim_culture;
DROP TABLE IF EXISTS dim_temps;
DROP TABLE IF EXISTS dim_modele;
SET FOREIGN_KEY_CHECKS = 1;

-- ---------- Dim_Commune 
CREATE TABLE dim_commune (
    id_commune    INT AUTO_INCREMENT PRIMARY KEY,
    code_insee    CHAR(5)       NOT NULL UNIQUE,      -- CHAR : « 05023 » garde son zéro
    nom_commune   VARCHAR(100)  NOT NULL,
    code_dept     VARCHAR(3)    NULL,
    nom_dept      VARCHAR(100)  NULL,
    code_region   VARCHAR(3)    NULL,
    nom_region    VARCHAR(100)  NULL,
    latitude      DECIMAL(8,5)  NOT NULL,
    longitude     DECIMAL(8,5)  NOT NULL,
    altitude_moy  INT           NULL,
    CONSTRAINT ck_commune_lat CHECK (latitude  BETWEEN -90  AND 90),
    CONSTRAINT ck_commune_lon CHECK (longitude BETWEEN -180 AND 180)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- Dim_Culture (référentiel de seuils — chaque seuil doit être sourcé)
CREATE TABLE dim_culture (
    id_culture                INT AUTO_INCREMENT PRIMARY KEY,
    nom                       VARCHAR(60)  NOT NULL UNIQUE,
    t_base_c                  DECIMAL(4,1) NOT NULL,  -- T° de base des GDD
    gdd_maturite_cj           INT          NULL,      -- NULL = non défini (olivier, pérenne)
    seuil_gel_c               DECIMAL(4,1) NOT NULL,  -- jour de gel si t_min < seuil
    besoin_eau_mm             INT          NOT NULL,
    t_opt_min_c               DECIMAL(4,1) NOT NULL,
    t_opt_max_c               DECIMAL(4,1) NOT NULL,
    seuil_stress_thermique_c  DECIMAL(4,1) NOT NULL,  -- jour de stress si t_max > seuil
    source                    VARCHAR(1000) NOT NULL, -- provenance (jamais « selon l'IA »)
    CONSTRAINT ck_culture_opt    CHECK (t_opt_min_c < t_opt_max_c),
    CONSTRAINT ck_culture_stress CHECK (seuil_stress_thermique_c >= t_opt_max_c),
    CONSTRAINT ck_culture_eau    CHECK (besoin_eau_mm > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- Dim_Temps : toute la plage de l'API (1950 -> 2050)
-- Deux niveaux de période dans la même table :
--   * des DÉCENNIES (1951-1960 ... 2041-2050) -> courbes d'évolution sur tout 1950-2050 ;
--   * deux HORIZONS de 30 ans (est_horizon = TRUE) -> comparaison « référence vs projection ».
CREATE TABLE dim_temps (
    id_temps      INT AUTO_INCREMENT PRIMARY KEY,
    libelle       VARCHAR(40) NOT NULL UNIQUE,        -- « 1991-2020 »
    annee_debut   SMALLINT    NOT NULL,
    annee_fin     SMALLINT    NOT NULL,
    type_periode  ENUM('reference','projection') NOT NULL, -- 'reference' si annee_fin <= 2020, sinon 'projection'
    est_horizon   BOOLEAN     NOT NULL DEFAULT FALSE, -- TRUE = période de 30 ans comparée dans l'appli
    CONSTRAINT ck_temps        CHECK (annee_fin > annee_debut),
    CONSTRAINT ck_temps_bornes CHECK (annee_debut >= 1950 AND annee_fin <= 2050)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- Dim_Modele (modèle climatique ; JAMAIS écrit en dur dans le code)
-- Source : tableau « Climate Model / Origin / Run by / Resolution » de la doc Open-Meteo Climate API.
CREATE TABLE dim_modele (
    id_modele       INT AUTO_INCREMENT PRIMARY KEY,
    code_api        VARCHAR(40)  NOT NULL UNIQUE,   -- valeur du paramètre « models » de l'API
    origine         VARCHAR(40)  NULL,              -- pays / zone
    institution     VARCHAR(250) NULL,              -- « Run by »
    resolution_km   SMALLINT     NULL,
    a_humidite_sol  BOOLEAN      NOT NULL DEFAULT FALSE,  -- soil_moisture : seulement MRI et EC_Earth3P_HR
    actif           BOOLEAN      NOT NULL DEFAULT TRUE    -- FALSE = a renvoyé des données vides
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- Fact_Indicateur : le centre de l'étoile (indicateurs calculés, STOCKÉS)
-- id_session : isolation par visiteur + effacement RGPD ('global' = grille pré-calculée).
CREATE TABLE fact_indicateur (
    id_commune              INT          NOT NULL,
    id_culture              INT          NOT NULL,
    id_temps                INT          NOT NULL,
    id_modele               INT          NOT NULL,
    id_session              VARCHAR(64)  NOT NULL DEFAULT 'global',
    gdd_saison_cj           DECIMAL(8,1) NULL,  -- GDD moyens par an sur la saison
    maturite_atteinte_pct   DECIMAL(6,1) NULL,  -- gdd / gdd_maturite × 100 (NULL si non défini)
    jours_gel               DECIMAL(5,1) NULL,  -- jours/an avec t_min < seuil_gel (fenêtre sensible)
    jours_stress_thermique  DECIMAL(5,1) NULL,  -- jours/an avec t_max > seuil
    jours_t_optimale        DECIMAL(5,1) NULL,  -- jours/an avec t_moy dans [t_opt_min ; t_opt_max]
    pluie_saison_mm         DECIMAL(7,1) NULL,
    bilan_hydrique_mm       DECIMAL(7,1) NULL,  -- Σ(pluie − ET0 Hargreaves) sur la saison
    nb_annees_calculees     SMALLINT     NOT NULL,
    date_calcul             TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_commune, id_culture, id_temps, id_modele, id_session),
    CONSTRAINT fk_f_commune FOREIGN KEY (id_commune) REFERENCES dim_commune(id_commune),
    CONSTRAINT fk_f_culture FOREIGN KEY (id_culture) REFERENCES dim_culture(id_culture),
    CONSTRAINT fk_f_temps   FOREIGN KEY (id_temps)   REFERENCES dim_temps(id_temps),
    CONSTRAINT fk_f_modele  FOREIGN KEY (id_modele)  REFERENCES dim_modele(id_modele)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX ix_fact_session ON fact_indicateur (id_session);
CREATE INDEX ix_fact_culture ON fact_indicateur (id_culture, id_temps, id_modele);

-- ---------- Données de référence construites (pas de CSV source)
INSERT INTO dim_temps (libelle, annee_debut, annee_fin, type_periode, est_horizon) VALUES
  ('1991-2020', 1991, 2020, 'reference', 1),
  ('2021-2050', 2021, 2050, 'projection', 1),
  ('1951-1960', 1951, 1960, 'reference', 0),
  ('1961-1970', 1961, 1970, 'reference', 0),
  ('1971-1980', 1971, 1980, 'reference', 0),
  ('1981-1990', 1981, 1990, 'reference', 0),
  ('1991-2000', 1991, 2000, 'reference', 0),
  ('2001-2010', 2001, 2010, 'reference', 0),
  ('2011-2020', 2011, 2020, 'reference', 0),
  ('2021-2030', 2021, 2030, 'projection', 0),
  ('2031-2040', 2031, 2040, 'projection', 0),
  ('2041-2050', 2041, 2050, 'projection', 0);

-- Les 7 modèles de la documentation Open-Meteo. Fiche DEV (sept. 2026) : 6 fonctionnent pour la France ;
INSERT INTO dim_modele (code_api, origine, institution, resolution_km, a_humidite_sol, actif) VALUES
  ('CMCC_CM2_VHR4', 'Italie',   'Fondazione Centro Euro-Mediterraneo sui Cambiamenti Climatici, Lecce (CMCC)', 30, FALSE, TRUE),
  ('FGOALS_f3_H',   'Chine',    'Chinese Academy of Sciences, Beijing (CAS)', 28, FALSE, TRUE),
  ('HiRAM_SIT_HR',  'Taïwan',   'Research Center for Environmental Changes, Academia Sinica, Nankang, Taipei (AS-RCEC)', 25, FALSE, TRUE),
  ('MRI_AGCM3_2_S', 'Japon',    'Meteorological Research Institute, Tsukuba, Ibaraki (MRI)', 20, TRUE,  TRUE),
  ('EC_Earth3P_HR', 'Europe',   'EC-Earth consortium, Rossby Center, Swedish Meteorological and Hydrological Institute/SMHI, Norrkoping, Sweden', 29, TRUE, FALSE),
  ('MPI_ESM1_2_XR', 'Allemagne','Max Planck Institute for Meteorology, Hamburg 20146', 51, FALSE, TRUE),
  ('NICAM16_8S',    'Japon',    'Japan Agency for Marine-Earth Science and Technology, Kanagawa 236-0001 (MIROC)', 31, FALSE, TRUE);
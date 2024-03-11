-- Table: nexprimescmmgr.nsa_embedding_file

-- DROP TABLE IF EXISTS nexprimescmmgr.nsa_embedding_file;

CREATE TABLE IF NOT EXISTS nexprimescmmgr.nsa_embedding_file
(
    file_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    file_path character varying(255) COLLATE pg_catalog."default" NOT NULL,
    uuid uuid NOT NULL,
    create_datetime timestamp with time zone NOT NULL,
    create_user_id character varying(100) COLLATE pg_catalog."default" NOT NULL,
    modified_datetime timestamp with time zone NOT NULL,
    modified_user_id character varying(100) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT nsa_embedding_file_pkey PRIMARY KEY (file_id),
    CONSTRAINT nsa_embedding_file_create_user_id_fk FOREIGN KEY (create_user_id)
        REFERENCES nexprimescmmgr.nsa_user (user_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET DEFAULT,
    CONSTRAINT nsa_embedding_file_modified_user_id_fk FOREIGN KEY (modified_user_id)
        REFERENCES nexprimescmmgr.nsa_user (user_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET DEFAULT
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS nexprimescmmgr.nsa_embedding_file
    OWNER to nexprimescmmgr;
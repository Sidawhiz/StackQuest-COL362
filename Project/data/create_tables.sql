drop table if exists Users;
drop table if exists Questions;
drop table if exists Answers;
drop table if exists Tags;

CREATE TABLE Users(
    id bigint,
    display_name text,
    about_me text,
    age bigint,
    creation_date timestamptz,
    last_access_date timestamptz,
    location text,
    reputation bigint,
    up_votes bigint,
    down_votes bigint,
    views bigint,
    profile_image_url text,
    website_url text,
    CONSTRAINT users_pkey PRIMARY KEY (id)
);

CREATE TABLE Questions (
    Id bigint,
    OwnerUserId bigint,
    CreationDate timestamptz,
    Score bigint,
    Title text,
    Body text,
    CONSTRAINT questions_pkey PRIMARY KEY (Id),
    CONSTRAINT questions_fkey FOREIGN KEY (OwnerUserId) REFERENCES Users(id)
);

CREATE TABLE Answers(
    Id bigint,
    OwnerUserId bigint,
    CreationDate timestamptz,
    ParentId bigint,
    Score bigint,
    Body text,
    CONSTRAINT answers_pkey PRIMARY KEY (Id),
    CONSTRAINT answers_user_fkey FOREIGN KEY (OwnerUserId) REFERENCES Users(id),
    CONSTRAINT answers_question_fkey FOREIGN KEY (ParentId) REFERENCES Questions(Id)
);

CREATE TABLE Tags(
    id bigint,
    tag text,
    CONSTRAINT tags_question_fkey FOREIGN KEY (id) REFERENCES Questions(Id)
);


COPY Users from '/Users/manaskopparicloud.com/Desktop/Project/data/Users.csv' DELIMITER ',' CSV HEADER;
COPY Questions from '/Users/manaskopparicloud.com/Desktop/Project/data/Questions.csv' DELIMITER ',' CSV HEADER ;
COPY Answers from '/Users/manaskopparicloud.com/Desktop/Project/data/Answers.csv' DELIMITER ',' CSV HEADER;
COPY Tags from '/Users/manaskopparicloud.com/Desktop/Project/data/Tags.csv'  DELIMITER ',' CSV HEADER;

CREATE INDEX idx1 ON answers(parentid);
CREATE INDEX idx2 ON tags(tag);



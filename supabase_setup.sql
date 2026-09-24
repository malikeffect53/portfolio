-- =============================================================
-- Supabase PostgreSQL Setup & Migration for Burhanuddin Malik
-- Run this script in the Supabase SQL Editor
-- =============================================================

-- 1. Tables Creation
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    name TEXT,
    email TEXT DEFAULT '',
    role TEXT NOT NULL,
    pw TEXT NOT NULL,
    sections TEXT DEFAULT '[]',
    active INTEGER DEFAULT 1,
    created TEXT,
    updated TEXT DEFAULT '',
    last_login TEXT
);

CREATE TABLE IF NOT EXISTS items (
    id BIGSERIAL PRIMARY KEY,
    kind TEXT NOT NULL,
    slug TEXT NOT NULL,
    title TEXT NOT NULL,
    data JSONB DEFAULT '{}'::jsonb,
    status TEXT DEFAULT 'published',
    access TEXT DEFAULT 'A',
    pos INTEGER DEFAULT 0,
    created TEXT,
    updated TEXT
);
CREATE INDEX IF NOT EXISTS ix_items_kind_status ON items(kind, status);

CREATE TABLE IF NOT EXISTS hits (
    id BIGSERIAL PRIMARY KEY,
    ts TEXT,
    day TEXT,
    vid TEXT,
    path TEXT,
    kind TEXT,
    slug TEXT,
    src TEXT,
    device TEXT,
    secs REAL DEFAULT 0,
    sid TEXT
);
CREATE INDEX IF NOT EXISTS ix_hits_day ON hits(day);
CREATE INDEX IF NOT EXISTS ix_hits_sid ON hits(sid);

CREATE TABLE IF NOT EXISTS feedback (
    id BIGSERIAL PRIMARY KEY,
    ts TEXT,
    design INT,
    content INT,
    navigation INT,
    overall INT,
    comment TEXT
);

CREATE TABLE IF NOT EXISTS contacts (
    id BIGSERIAL PRIMARY KEY,
    ts TEXT,
    name TEXT,
    email TEXT,
    message TEXT,
    read INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS activity (
    id BIGSERIAL PRIMARY KEY,
    ts TEXT,
    actor TEXT,
    action TEXT,
    obj TEXT,
    area TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS passcodes (
    id BIGSERIAL PRIMARY KEY,
    label TEXT,
    role TEXT,
    pw TEXT,
    sections TEXT DEFAULT '[]',
    active INTEGER DEFAULT 1,
    ver TEXT,
    created TEXT,
    last_used TEXT,
    uses INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS settings (
    k TEXT PRIMARY KEY,
    v TEXT
);

CREATE TABLE IF NOT EXISTS backups (
    id BIGSERIAL PRIMARY KEY,
    ts TEXT,
    name TEXT UNIQUE,
    kind TEXT,
    size BIGINT,
    status TEXT,
    note TEXT
);

CREATE TABLE IF NOT EXISTS media (
    id BIGSERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    original_name TEXT,
    ext TEXT,
    size BIGINT,
    is_private INT DEFAULT 0,
    title TEXT DEFAULT '',
    caption TEXT DEFAULT '',
    alt TEXT DEFAULT '',
    project TEXT DEFAULT '',
    pos INTEGER DEFAULT 0,
    created TEXT,
    content_b64 TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS ix_media_ext ON media(ext);

-- 2. Seed Current Data

-- Users Seed
INSERT INTO users (id, username, name, role, pw, sections, active, created, last_login, updated, email) VALUES (1, 'owner', 'Burhanuddin', 'owner', 'scrypt:32768:8:1$PhW7WuWamh7kNqp7$3dcc05e4a1f407c1a7d252b15751823533c1c45dfb6e1c4a2e67cf286b1100cc228178762a5d010122e47089b1ea226f2d78017488191c11811b3ad7ea7c60eb', '[]', 1, '2026-09-22T19:45:39Z', '2026-09-23T18:23:57Z', '', '') ON CONFLICT (username) DO NOTHING;

-- Settings Seed
INSERT INTO settings (k, v) VALUES ('home_name', 'Burhanuddin Malik') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('home_tagline', 'Creating with Purpose. Exploring with Curiosity. Growing with Every Journey.') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('about_who_text', 'I’m an artist, a learner and a future entrepreneur. I was born in Mumbai, brought up in Indore, and I now study B.Com at Burhani College.

My interests move between art, Arabic calligraphy, technology, AI, communication, public speaking, psychology, business and entrepreneurship. One theme runs through all of them: learning through doing.') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('archive_status', 'enabled') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('archive_title', 'Private Archive | Burhanuddin Malik (Verified)') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('archive_welcome', 'Welcome to my verified private archive.') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('archive_session_hours', '48') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('archive_default_role', 'B') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('archive_password_hash', 'scrypt:32768:8:1$iq9kLsmU3xRbIC4Z$117c5d8fa46b22583ddd66d8e44af6e36e3aba1eda433f34f4a70378bf7b7409957cff30e2a7afee3f5f3afcfcb3cd6a0b0bcb3d118fef8bef6cee42751fe3ac') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('archive_password_changed_at', '2026-09-23T18:48:01Z') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('archive_password_ver', '1d7c9f96bdf296a9') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('hero_photo', '') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('home_intro', 'I’m Burhanuddin Malik — a creative learner and curious explorer with a growing interest in art, communication, technology, and entrepreneurship. This portfolio brings together the work, experiences, and ideas that continue to shape my journey.') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('home_btn1_label', 'Explore My Work') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('home_btn1_link', '/work') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('home_btn2_label', 'Explore My Journey') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('home_btn2_link', '/journey') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('home_feat_title', 'Featured work') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('home_band_title', 'Explore my journey') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('home_band_text', 'From Mumbai and Indore to Aljamea, from a first sketch to large-scale paintings, and now business and technology. Each chapter has its own story.') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('home_quote', 'A journey shaped by curiosity, creativity, and continuous learning.') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('home_quote_body', 'I used to be shy and reserved. Time at Aljamea helped me grow comfortable with crowds, communication, questions and responsibility. Today art, calligraphy, technology and business all shape how I learn.') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('home_blog_title', 'Latest articles') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('home_contact_title', 'Let’s talk about art, ideas, or something you’re building.') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('about_photo', '') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('about_growth_photo', '') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('about_title', 'A journey shaped by curiosity, creativity, and continuous learning.') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('about_interests', '["[\"Art\"","\"Arabic calligraphy\"","\"Technology\"","\"AI\"","\"Communication\"","\"Public speaking\"","\"Psychology\"","\"Business\"","\"Entrepreneurship\"","\"Learning\"","\"Personal growth\"]"]') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('about_growth_text', 'I was shy, reserved and introverted. Joining Aljamea-tus-Saifiyah Surat put me among larger groups and new people, with new responsibilities: communication, collaboration, public speaking and everyday social interaction.

It wasn’t an overnight change. Comfort came gradually, through one conversation, one role and one responsibility at a time. One lesson stayed with me: asking questions is part of learning, not a sign of weakness.') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('about_creativity_text', 'It began around Standard 4 with a small A5 sunset painting made in a painting class, which my teacher appreciated. That grew gradually into sketching, painting, large canvases, Arabic handwriting, calligraphy and Maaraz decoration.

Khat has become both a technical and an intellectual discipline for me, especially through a two-month course on Thuluth from Misr.') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('about_curiosity_text', 'Psychology, technology, AI and business keep me asking questions. I’m learning Python, Django and web development, and exploring how AI can help me build things. These are areas I’m learning, not areas I’ve mastered.') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('about_drives_text', 'Helping others, patience, calmness, continuous learning and creativity.') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('about_education_items', '[["[[\"73%\",\"10th\"],[\"76%\",\"12th, Commerce\"],[\"B.Com\",\"Burhani College, current\"]]",""]]') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('about_education_path', 'A convent school in Mumbai for pre-primary, then MSB Educational Institute in Indore until Grade 9, then Aljamea-tus-Saifiyah Surat for about four years, and later Aljamea-tus-Saifiyah Marol.') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;
INSERT INTO settings (k, v) VALUES ('about_learning_items', '["[\"Khat\"","\"Tazheeb\"","\"AI\"","\"Python\"","\"Django\"","\"Web development\"","\"Communication\"","\"Psychology\"","\"Business\"","\"Entrepreneurship\"]"]') ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v;

-- Portfolio & Archive Items Seed
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (1, 'project', 'zareeh-mubarak', 'Zareeh Mubarak', '{"cat": "Paintings", "year": "1448", "featured": true, "short": "A massive canvas painting inspired by the Zareeh Mubarak of Moulana Ali AS in Najaf. About five months, over 100 hours.", "cover": "", "images": [], "facts": [["Duration", "About 5 months"], ["Effort", "100+ hours"], ["Medium", "Large canvas"], ["Intended for", "Saalat uz Zahab, Aljamea-tus-Saifiyah Marol, inshallah"]], "overview": "A massive canvas painting replicating the Zareeh Mubarak of Moulana Ali AS in Najaf. It took about five months and more than 100 hours of work, and it is intended, inshallah, for Saalat uz Zahab at Aljamea-tus-Saifiyah Marol.", "story": "The actual architecture and beauty of the Zareeh cannot truly be replicated. This painting is an attempt to carry a reflection of that beauty onto canvas.\n\nI was thousands of kilometres away from Najaf, and while painting, each stroke created a feeling of being closer to the Zareeh. There were periods of frustration and demotivation when I wanted to stop. The subject itself kept giving me motivation to continue.", "process": "", "timeline": [], "techniques": ["Layering", "Glazing", "Careful replication", "Shade matching", "Intricate grape motifs"], "challenges": ["Changing shades", "Matching colours", "Maintaining accuracy", "Managing a very large artwork", "Maintaining patience", "Handling extremely fine details"], "result": "The painting was completed, and finishing it increased my confidence.", "learned": "Patience became a personal strength. Finishing something this large taught me that steady, patient work can carry a project through its hardest stretches.", "sections": [["Overview", "A massive canvas painting replicating the Zareeh Mubarak of Moulana Ali AS in Najaf. It took about five months and more than 100 hours of work, and it is intended, inshallah, for Saalat uz Zahab at Aljamea-tus-Saifiyah Marol."], ["The Story", "The actual architecture and beauty of the Zareeh cannot truly be replicated. This painting is an attempt to carry a reflection of that beauty onto canvas.\n\nI was thousands of kilometres away from Najaf, and while painting, each stroke created a feeling of being closer to the Zareeh. There were periods of frustration and demotivation when I wanted to stop. The subject itself kept giving me motivation to continue."], ["More than a technical exercise", "The painting became connected with remembrance, yearning, reflection, seeking bounties and ibadat. Each stroke was experienced as a quiet form of all of these.\n\nI hope the artwork can remind viewers of Moulana Ali AS and the Zareeh Mubarak, create tranquility and hope, serve as a wasila for people unable to visit Najaf, and eventually contribute to the visual environment of Saalat uz Zahab."], ["Inspiration", "I was also inspired by the 13th Ashara Mubaraka in London and the discussion around the hunar (talents) of Mumineen."], ["Inscriptions", "The crown carries the Qasida Mubarak of Syedna Abdulqadir Najmuddin RA. Another inscription carries the Qasida Mubarak of Syedna Aali Qadar Mufaddal Saifuddin TUS."]], "arabic": "", "roleList": [], "interactive": ""}'::jsonb, 'published', 'A', 1, '2026-09-22T19:45:39Z', '2026-09-23T19:16:50Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (2, 'project', 'darajah-haadi-ashara-backdrop', 'Darajah Haadi Ashara Backdrop', '{"cat": "Paintings", "year": "1446H", "featured": true, "short": "A large-scale backdrop painted as a duo for Imtehaan Safahi 1446 and presented before His Holiness Syedna Mufaddal Saifuddin TUS.", "cover": "", "images": [], "facts": [["Occasion", "Imtehaan Safahi 1446"], ["Team", "Duo project"], ["Scale", "Large-scale backdrop"], ["Presented to", "His Holiness Syedna Mufaddal Saifuddin TUS"]], "sections": [["Overview", "A large-scale backdrop painting created during Imtehaan Safahi 1446. My partner and I drew from scratch, painted, and replicated the reference, working together throughout the process."], ["Beginning", "This was my first major large-scale painting after my small A5 sunset painting. I was nervous about the scale at first."], ["Working as a Duo", "We shared the whole process, from the first drawing to the final refinement. In my own words: I made a friendship between my hands and brushes."], ["Creating the Backdrop", "We drew from scratch, painted, and replicated a reference, working together throughout."], ["Learning to Work at Scale", "The large scale made me nervous at first. The experience built my confidence."], ["Presentation", "The backdrop was presented before His Holiness Syedna Mufaddal Saifuddin TUS, a major achievement for us."], ["Reflection", "This project was about collaboration, scale, confidence, responsibility and recognition. I described it as making a friendship between my hands and brushes."]], "timeline": ["Reference", "Drawing", "Painting", "Refinement", "Completion", "Presentation"], "techniques": ["Drawing from scratch", "Replicating a reference", "Large-scale painting"], "challenges": ["Working at a scale I had never attempted", "Coordinating as a duo"], "result": "Completed and presented before His Holiness.", "learned": "Collaboration, confidence at scale, and how much a partnership can lift creative work.", "arabic": "", "interactive": "", "roleList": []}'::jsonb, 'published', 'A', 2, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (3, 'project', 'faith-and-worldly-realm', 'Faith & Worldly Realm', '{"cat": "Paintings", "year": "1447H", "featured": true, "short": "An acrylic painting of an eye holding two twin brothers, Faith and Worldly Realm, in harmony.", "cover": "", "images": [], "facts": [["Year", "1447H"], ["Medium", "Acrylic"], ["Subject", "A human eye"]], "sections": [["Overview", "An acrylic painting of a human eye, created in 1447H. Inside the pupil, twin brothers named Faith and Worldly Realm sit back-to-back. The iris is divided into two radiant halves, one for divine serenity and one for worldly allure."], ["Concept", "The work was inspired by a bait of Syedna Taher Saifuddin RA. Its core idea is harmony rather than conflict. Faith illuminates the world, and the world gives faith form. From the right perspective they are twin reflections of one truth."], ["Reflection", "I felt blessed with the nazar of Aaqa Moula TUS."]], "timeline": [], "techniques": ["Acrylic painting"], "challenges": [], "result": "", "learned": "", "arabic": "", "interactive": "eye", "roleList": []}'::jsonb, 'published', 'A', 3, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (4, 'project', 'maaraz-ilmi-1447h', 'Maaraz Ilmi 1447H', '{"cat": "Maaraz", "year": "1447H", "featured": true, "short": "I led the Decoration Team: calligraphy, a painted 3D model of Yemen, a Yemeni costume and a speech.", "cover": "", "images": [], "facts": [["Year", "1447H"], ["Role", "In charge of the Decoration Team"], ["Theme", "The 12 constellations addressed by Aaqa Moula in Ashara Mubaraka 1447H"]], "sections": [["Overview", "Maaraz Ilmi 1447H was a large educational and creative exhibition project. I was in charge of the Decoration Team."], ["Concept", "The theme was the 12 constellations addressed by Aaqa Moula in Ashara Mubaraka 1447H."], ["My Role", "I led the Decoration Team and shaped the artistic direction. Tap the My role button above for the full list."], ["Decoration Team", "Decoration was a team effort. Leading it meant coordinating people as well as making things myself."], ["Calligraphy", "I wrote the main Maaraz name, and the main charts are in my own handwriting."], ["3D Yemen Model", "We created a large 3D physical map of Yemen, and I painted the model."], ["Costume & Presentation", "I wore a Yemeni costume as part of the storytelling."], ["Public Speaking", "I gave a speech."], ["Teamwork", "The project depended on teamwork, from decoration to presentation."], ["Result", "This project demonstrates leadership, artistic direction, calligraphy, handwriting, painting, model-making, cultural storytelling, public speaking and teamwork."]], "timeline": [], "techniques": ["Arabic handwriting", "Painting", "Model-making"], "challenges": [], "result": "", "learned": "", "arabic": "قبس اشعة النجوم الساطعة من برج اليمن اللامعة", "interactive": "", "roleList": ["Led the Decoration Team", "Wrote the main Maaraz name", "Wrote the main charts in my own handwriting", "Created a large 3D physical map of Yemen and painted the model", "Wore a Yemeni costume", "Gave a public speech"]}'::jsonb, 'published', 'A', 4, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (5, 'project', 'planetarium-maaraz', 'Planetarium Maaraz', '{"cat": "Maaraz", "year": "", "featured": false, "short": "A cardboard dome, a dark environment, projected stars, and Qur''anic ayat in gold on black chart paper.", "cover": "", "images": [], "facts": [["Where", "Aljamea Surat"], ["Role", "Head of a segment"]], "sections": [["Overview", "A Maaraz Ilmi at Aljamea Surat, created before the Darajah Haadi Ashara backdrop. I was head of a segment. My team created a dome from cardboard, painted it black and placed it in a dark environment. Stars and constellations were presented using a projector."], ["Calligraphy", "I wrote Qur''anic ayat in large Arabic calligraphy on black chart paper using gold paint. The writing became a major visual attraction because it shone in the dark."], ["Recognition", "I received the sharaf of representing the project before His Holiness. My calligraphy was praised by Mukassir-o-Dawat-il-Haq Syedi Malekul Ashtar BS Shujauddin."]], "timeline": [], "techniques": ["Arabic calligraphy", "Painting", "Decoration"], "challenges": [], "result": "", "learned": "Leadership, creative problem-solving and teamwork.", "arabic": "", "interactive": "", "roleList": []}'::jsonb, 'published', 'A', 5, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (6, 'project', 'learning-thuluth', 'Learning Thuluth', '{"cat": "Khat", "year": "", "featured": false, "short": "A two-month Khat course from Misr focused on Thuluth, with personal checking by an experienced Ustaaz.", "cover": "", "images": [], "facts": [["Course", "Two-month Khat course from Misr"], ["Focus", "Thuluth"], ["Feedback", "Personal checking by the Ustaaz"]], "sections": [["Overview", "A two-month Khat course from Misr with a detailed study of Thuluth."], ["Learning with an Ustaaz", "The Ustaaz had more than 45 years of experience. He checked my work personally, and his comments and appreciation were a big part of the learning."], ["Beyond technique", "The course had philosophical and conceptual dimensions as well as technical ones. For me, Khat is both a technical discipline and an intellectual one."]], "timeline": [], "techniques": ["Thuluth", "Personal correction", "Study and practice"], "challenges": [], "result": "", "learned": "", "arabic": "", "interactive": "", "roleList": []}'::jsonb, 'published', 'A', 6, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (7, 'journey', 'mumbai', 'Mumbai: Where It Began', '{"period": "Early years", "short": "Born in Mumbai, with pre-primary education at a convent school.", "story": "I was born in Mumbai and attended a convent school named diamond jubilee high school for pre-primary education.", "points": [], "areas": [], "closing": "", "image": ""}'::jsonb, 'published', 'A', 0, '2026-09-22T19:45:39Z', '2026-09-23T19:14:33Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (8, 'journey', 'indore', 'Indore: Growing Up', '{"period": "Childhood", "short": "Grew up in Indore and studied at MSB Educational Institute until Grade 9.", "story": "I was brought up in Indore. I studied at MSB Educational Institute until Grade 9.", "image": "", "points": [], "areas": [], "closing": ""}'::jsonb, 'published', 'A', 1, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (9, 'journey', 'aljamea-surat', 'Aljamea Surat: A New Chapter', '{"period": "About four years", "short": "Joined after the first two months of Grade 9. Four years of education and personal growth.", "story": "After the first two months of Grade 9, I joined Aljamea-tus-Saifiyah Surat and studied there for about four years. My studies included Kutub ud Da''wat, Deeni subjects and Uloom Kawniyah, the exact sciences in light of Al-Quran.\n\nI had been shy and introverted. Larger groups, new people, communication and responsibility slowly became part of everyday life. There were days when concepts felt hard while classmates seemed to grasp them instantly, and because of my shyness, asking basic questions felt difficult. Comfortable friendships later helped me ask, and clarify the fundamentals.\n\nThat became an important lesson: asking questions is part of learning, not a sign of weakness.", "image": "", "points": [], "areas": [], "closing": ""}'::jsonb, 'published', 'A', 2, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (10, 'journey', 'online-first-year', 'Online First Year: Learning Differently', '{"period": "First year", "short": "Pandemic-era online education, and a few discoveries.", "story": "My first year at Aljamea was online because of the pandemic. Learning from home became a period of discovery.", "image": "", "points": ["Arabic typing", "Art", "Sketching", "Independent learning"], "areas": [], "closing": ""}'::jsonb, 'published', 'A', 3, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (11, 'journey', 'aljamea-marol', 'Aljamea Marol: Another Chapter', '{"period": "Later years", "short": "Continued education and grew in confidence and communication.", "story": "I continued my education at the Aljamea-tus-Saifiyah Marol branch. It was another stage of education, communication, social confidence, responsibility and personal growth.", "image": "", "points": [], "areas": [], "closing": ""}'::jsonb, 'published', 'A', 4, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (12, 'journey', 'art', 'Art: From Small Beginnings', '{"period": "Ongoing", "short": "From an A5 sunset painting to larger projects.", "story": "Art began around Standard 4 with a small A5 sunset painting made in a painting class. My teacher appreciated it, and that small moment sparked a longer journey.\n\nIt grew gradually, not all at once.", "image": "", "points": ["Sketching", "Painting", "Large canvases", "Arabic handwriting", "Arabic calligraphy", "Maaraz decoration", "Large-scale creative work", "Conceptual artwork"], "areas": [], "closing": ""}'::jsonb, 'published', 'A', 5, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (13, 'journey', 'khat', 'Khat: Discipline Through Form', '{"period": "Ongoing", "short": "Arabic calligraphy through study and practice.", "story": "A two-month Khat course from Misr gave me a detailed study of Thuluth. The Ustaaz, who had more than 45 years of experience, checked my work personally and offered comments and appreciation.\n\nThe course had philosophical and conceptual dimensions too. For me, Khat is both a technical discipline and an intellectual one.", "image": "", "points": [], "areas": [], "closing": ""}'::jsonb, 'published', 'A', 6, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (14, 'journey', 'creating-and-leading', 'Creating & Leading', '{"period": "Projects", "short": "Four major creative projects, each with its own lesson.", "story": "These projects taught me patience, collaboration, harmony of ideas and leadership.", "image": "", "points": ["Planetarium Maaraz", "Darajah Haadi Ashara backdrop", "Maaraz Ilmi 1447H", "Zareeh Mubarak"], "areas": [], "closing": ""}'::jsonb, 'published', 'A', 7, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (15, 'journey', 'bcom', 'B.Com', '{"period": "Now", "short": "B.Com at Burhani College, with interests widening.", "story": "I am pursuing B.Com at Burhani College. My interests are widening toward business, entrepreneurship, communication and technology.", "image": "", "points": ["Business", "Entrepreneurship", "Communication", "Technology"], "areas": [], "closing": ""}'::jsonb, 'published', 'A', 8, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (16, 'journey', 'technology-and-ai', 'Technology & AI', '{"period": "Now", "short": "Learning to build with Python, Django, web development and AI.", "story": "I am learning to build. Python, Django, web development and AI are areas I am exploring and experimenting with, not areas I have mastered. This website is itself one of my learning projects, built with AI assistance.", "image": "", "points": ["Python", "Django", "Web development", "AI"], "areas": [], "closing": ""}'::jsonb, 'published', 'A', 9, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (17, 'journey', 'today', 'Today', '{"period": "Today", "short": "Creative, intellectual, technical and entrepreneurial.", "story": "Four areas of one identity, all still growing.", "image": "", "points": [], "areas": [["Creative", "Art, Khat and design"], ["Intellectual", "Learning, psychology and knowledge"], ["Technical", "Python, Django and AI, all still being learned"], ["Entrepreneurial", "Business ideas and digital projects"]], "closing": ""}'::jsonb, 'published', 'A', 10, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (18, 'journey', 'whats-next', 'What''s Next', '{"period": "Next", "short": "Deeper Khat, Tazheeb, technology, entrepreneurship and more.", "story": "Where I want to go from here:", "image": "", "points": ["Deeper Khat", "Tazheeb", "AI and technology", "Entrepreneurship", "Creative projects", "Continuous learning"], "areas": [], "closing": "The journey continues."}'::jsonb, 'published', 'A', 11, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (19, 'achievement', 'a1', 'Two-month Khat course (Thuluth)', '{"cat": "Artistic", "details": "Studied Thuluth in detail on a two-month Khat course from Misr, with personal checking, comments and appreciation from an Ustaaz of more than 45 years of experience.", "project": "learning-thuluth", "learned": "", "recognition": "", "image": ""}'::jsonb, 'published', 'A', 1, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (20, 'achievement', 'a2', 'CorelDRAW Certification', '{"cat": "Certifications", "details": "A certification in CorelDRAW.", "project": "", "learned": "", "recognition": "", "image": ""}'::jsonb, 'published', 'A', 2, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (21, 'achievement', 'a3', 'District-level Roll Ball', '{"cat": "Sports", "details": "Played Roll Ball at district level.", "project": "", "learned": "", "recognition": "", "image": ""}'::jsonb, 'published', 'A', 3, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (22, 'achievement', 'a4', 'Captain, Roll Ball team', '{"cat": "Sports", "details": "Captained the team.", "project": "", "learned": "", "recognition": "", "image": ""}'::jsonb, 'published', 'A', 4, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (23, 'achievement', 'a5', 'Head of the Decoration Team, Maaraz Ilmi 1447H', '{"cat": "Leadership", "details": "Led the Decoration Team, wrote the Maaraz name and main charts, built a painted 3D model of Yemen, and gave a speech.", "project": "maaraz-ilmi-1447h", "learned": "", "recognition": "", "image": ""}'::jsonb, 'published', 'A', 5, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (24, 'achievement', 'a6', 'Head of a segment, Planetarium Maaraz', '{"cat": "Leadership", "details": "Led a segment at Aljamea Surat: a cardboard dome, a dark environment, projected stars and gold calligraphy.", "project": "planetarium-maaraz", "learned": "", "recognition": "", "image": ""}'::jsonb, 'published', 'A', 6, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (25, 'achievement', 'a7', 'Presented the Darajah Haadi Ashara Backdrop', '{"cat": "Presentations", "details": "Our duo backdrop was presented before His Holiness Syedna Mufaddal Saifuddin TUS.", "project": "darajah-haadi-ashara-backdrop", "learned": "", "recognition": "", "image": ""}'::jsonb, 'published', 'A', 7, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (26, 'achievement', 'a8', 'Calligraphy praised, Planetarium Maaraz', '{"cat": "Recognition", "details": "Had the sharaf of representing the project before His Holiness, and my calligraphy was praised by Mukassir-o-Dawat-il-Haq Syedi Malekul Ashtar BS Shujauddin.", "project": "planetarium-maaraz", "learned": "", "recognition": "", "image": ""}'::jsonb, 'published', 'A', 8, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (27, 'post', 'learning-khat', 'Learning Khat', '{"category": "Khat", "excerpt": "Patience, practice and perspective.", "cover": "", "body": "", "soon": true, "related": "learning-thuluth", "date": ""}'::jsonb, 'published', 'A', 0, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (28, 'post', 'from-shyness-to-expression', 'From Shyness to Expression', '{"category": "Reflections", "excerpt": "Communication and personal growth.", "cover": "", "body": "", "soon": true, "related": "aljamea-surat", "date": ""}'::jsonb, 'published', 'A', 1, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (29, 'post', 'from-an-a5-sunset-to-large-scale-art', 'From an A5 Sunset to Large-Scale Art', '{"category": "Reflections", "excerpt": "The evolution of creativity.", "cover": "", "body": "", "soon": true, "related": "art, darajah-haadi-ashara-backdrop, zareeh-mubarak", "date": ""}'::jsonb, 'published', 'A', 2, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (30, 'post', 'learning-to-build-with-ai', 'Learning to Build with AI', '{"category": "AI", "excerpt": "AI, Python, Django and technology learning.", "cover": "", "body": "", "soon": true, "related": "technology-and-ai", "date": ""}'::jsonb, 'published', 'A', 3, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (31, 'post', 'learning-to-think-like-a-builder', 'Learning to Think Like a Builder', '{"category": "Business", "excerpt": "B.Com, business and entrepreneurship.", "cover": "", "body": "", "soon": true, "related": "bcom", "date": ""}'::jsonb, 'published', 'A', 4, '2026-09-22T19:45:39Z', '2026-09-22T19:45:39Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (32, 'artwork', 'tazheeb', 'Tazheeb', '{"year": "1447", "details": "", "image": ""}'::jsonb, 'draft', 'C', 0, '2026-09-23T18:55:33Z', '2026-09-23T18:55:33Z') ON CONFLICT (id) DO NOTHING;
INSERT INTO items (id, kind, slug, title, data, status, access, pos, created, updated) VALUES (33, 'artwork', 'khat-un-naskh', 'Khat un naskh', '{"year": "1447", "details": "moula ne araz kidu hatu al imtehaan us sanawi ma 1447 marol, jamea saifiyah", "image": ""}'::jsonb, 'draft', 'C', 0, '2026-09-23T18:56:30Z', '2026-09-23T18:56:30Z') ON CONFLICT (id) DO NOTHING;

-- 3. Reset ID sequences to avoid conflict with seeded IDs
SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 1));
SELECT setval('items_id_seq', COALESCE((SELECT MAX(id) FROM items), 1));
SELECT setval('hits_id_seq', COALESCE((SELECT MAX(id) FROM hits), 1));
SELECT setval('feedback_id_seq', COALESCE((SELECT MAX(id) FROM feedback), 1));
SELECT setval('contacts_id_seq', COALESCE((SELECT MAX(id) FROM contacts), 1));
SELECT setval('activity_id_seq', COALESCE((SELECT MAX(id) FROM activity), 1));
SELECT setval('passcodes_id_seq', COALESCE((SELECT MAX(id) FROM passcodes), 1));
SELECT setval('backups_id_seq', COALESCE((SELECT MAX(id) FROM backups), 1));
SELECT setval('media_id_seq', COALESCE((SELECT MAX(id) FROM media), 1));

-- 4. Enable Row Level Security (RLS) on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE hits ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE passcodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE backups ENABLE ROW LEVEL SECURITY;
ALTER TABLE media ENABLE ROW LEVEL SECURITY;


# Starter content. It is loaded into the database once, on the very first run.
# After that, everything is managed from the admin portal (/admin).

def P(slug, title, cat, year, featured, short, facts, sections, techniques=(), challenges=(),
      result="", learned="", arabic="", interactive="", roleList=(), pos=0, timeline=()):
    return dict(kind="project", slug=slug, title=title, pos=pos, data=dict(
        cat=cat, year=year, featured=featured, short=short, cover="", images=[],
        facts=[list(f) for f in facts], sections=[list(s) for s in sections],
        timeline=list(timeline), techniques=list(techniques), challenges=list(challenges),
        result=result, learned=learned, arabic=arabic, interactive=interactive,
        roleList=list(roleList)))

PROJECTS = [
    P("zareeh-mubarak", "Zareeh Mubarak", "Paintings", "", True,
      "A massive canvas painting inspired by the Zareeh Mubarak of Moulana Ali AS in Najaf. About five months, over 100 hours.",
      [("Duration", "About 5 months"), ("Effort", "100+ hours"), ("Medium", "Large canvas"),
       ("Intended for", "Saalat uz Zahab, Aljamea-tus-Saifiyah Marol, inshallah")],
      [("Overview", "A massive canvas painting replicating the Zareeh Mubarak of Moulana Ali AS in Najaf. It took about five months and more than 100 hours of work, and it is intended, inshallah, for Saalat uz Zahab at Aljamea-tus-Saifiyah Marol."),
       ("The Story", "The actual architecture and beauty of the Zareeh cannot truly be replicated. This painting is an attempt to carry a reflection of that beauty onto canvas.\n\nI was thousands of kilometres away from Najaf, and while painting, each stroke created a feeling of being closer to the Zareeh. There were periods of frustration and demotivation when I wanted to stop. The subject itself kept giving me motivation to continue."),
       ("More than a technical exercise", "The painting became connected with remembrance, yearning, reflection, seeking bounties and ibadat. Each stroke was experienced as a quiet form of all of these.\n\nI hope the artwork can remind viewers of Moulana Ali AS and the Zareeh Mubarak, create tranquility and hope, serve as a wasila for people unable to visit Najaf, and eventually contribute to the visual environment of Saalat uz Zahab."),
       ("Inspiration", "I was also inspired by the 13th Ashara Mubaraka in London and the discussion around the hunar (talents) of Mumineen."),
       ("Inscriptions", "The crown carries the Qasida Mubarak of Syedna Abdulqadir Najmuddin RA. Another inscription carries the Qasida Mubarak of Syedna Aali Qadar Mufaddal Saifuddin TUS.")],
      ["Layering", "Glazing", "Careful replication", "Shade matching", "Intricate grape motifs"],
      ["Changing shades", "Matching colours", "Maintaining accuracy", "Managing a very large artwork",
       "Maintaining patience", "Handling extremely fine details"],
      "The painting was completed, and finishing it increased my confidence.",
      "Patience became a personal strength. Finishing something this large taught me that steady, patient work can carry a project through its hardest stretches.",
      pos=1),
    P("darajah-haadi-ashara-backdrop", "Darajah Haadi Ashara Backdrop", "Paintings", "1446H", True,
      "A large-scale backdrop painted as a duo for Imtehaan Safahi 1446 and presented before His Holiness Syedna Mufaddal Saifuddin TUS.",
      [("Occasion", "Imtehaan Safahi 1446"), ("Team", "Duo project"), ("Scale", "Large-scale backdrop"),
       ("Presented to", "His Holiness Syedna Mufaddal Saifuddin TUS")],
      [("Overview", "A large-scale backdrop painting created during Imtehaan Safahi 1446. My partner and I drew from scratch, painted, and replicated the reference, working together throughout the process."),
       ("Beginning", "This was my first major large-scale painting after my small A5 sunset painting. I was nervous about the scale at first."),
       ("Working as a Duo", "We shared the whole process, from the first drawing to the final refinement. In my own words: I made a friendship between my hands and brushes."),
       ("Creating the Backdrop", "We drew from scratch, painted, and replicated a reference, working together throughout."),
       ("Learning to Work at Scale", "The large scale made me nervous at first. The experience built my confidence."),
       ("Presentation", "The backdrop was presented before His Holiness Syedna Mufaddal Saifuddin TUS, a major achievement for us."),
       ("Reflection", "This project was about collaboration, scale, confidence, responsibility and recognition. I described it as making a friendship between my hands and brushes.")],
      ["Drawing from scratch", "Replicating a reference", "Large-scale painting"],
      ["Working at a scale I had never attempted", "Coordinating as a duo"],
      "Completed and presented before His Holiness.",
      "Collaboration, confidence at scale, and how much a partnership can lift creative work.", pos=2, timeline=["Reference", "Drawing", "Painting", "Refinement", "Completion", "Presentation"]),
    P("faith-and-worldly-realm", "Faith & Worldly Realm", "Paintings", "1447H", True,
      "An acrylic painting of an eye holding two twin brothers, Faith and Worldly Realm, in harmony.",
      [("Year", "1447H"), ("Medium", "Acrylic"), ("Subject", "A human eye")],
      [("Overview", "An acrylic painting of a human eye, created in 1447H. Inside the pupil, twin brothers named Faith and Worldly Realm sit back-to-back. The iris is divided into two radiant halves, one for divine serenity and one for worldly allure."),
       ("Concept", "The work was inspired by a bait of Syedna Taher Saifuddin RA. Its core idea is harmony rather than conflict. Faith illuminates the world, and the world gives faith form. From the right perspective they are twin reflections of one truth."),
       ("Reflection", "I felt blessed with the nazar of Aaqa Moula TUS.")],
      ["Acrylic painting"], interactive="eye", pos=3),
    P("maaraz-ilmi-1447h", "Maaraz Ilmi 1447H", "Maaraz", "1447H", True,
      "I led the Decoration Team: calligraphy, a painted 3D model of Yemen, a Yemeni costume and a speech.",
      [("Year", "1447H"), ("Role", "In charge of the Decoration Team"),
       ("Theme", "The 12 constellations addressed by Aaqa Moula in Ashara Mubaraka 1447H")],
      [("Overview", "Maaraz Ilmi 1447H was a large educational and creative exhibition project. I was in charge of the Decoration Team."),
       ("Concept", "The theme was the 12 constellations addressed by Aaqa Moula in Ashara Mubaraka 1447H."),
       ("My Role", "I led the Decoration Team and shaped the artistic direction. Tap the My role button above for the full list."),
       ("Decoration Team", "Decoration was a team effort. Leading it meant coordinating people as well as making things myself."),
       ("Calligraphy", "I wrote the main Maaraz name, and the main charts are in my own handwriting."),
       ("3D Yemen Model", "We created a large 3D physical map of Yemen, and I painted the model."),
       ("Costume & Presentation", "I wore a Yemeni costume as part of the storytelling."),
       ("Public Speaking", "I gave a speech."),
       ("Teamwork", "The project depended on teamwork, from decoration to presentation."),
       ("Result", "This project demonstrates leadership, artistic direction, calligraphy, handwriting, painting, model-making, cultural storytelling, public speaking and teamwork.")],
      ["Arabic handwriting", "Painting", "Model-making"],
      arabic="قبس اشعة النجوم الساطعة من برج اليمن اللامعة",
      roleList=["Led the Decoration Team", "Wrote the main Maaraz name", "Wrote the main charts in my own handwriting",
                "Created a large 3D physical map of Yemen and painted the model", "Wore a Yemeni costume", "Gave a public speech"], pos=4),
    P("planetarium-maaraz", "Planetarium Maaraz", "Maaraz", "", False,
      "A cardboard dome, a dark environment, projected stars, and Qur'anic ayat in gold on black chart paper.",
      [("Where", "Aljamea Surat"), ("Role", "Head of a segment")],
      [("Overview", "A Maaraz Ilmi at Aljamea Surat, created before the Darajah Haadi Ashara backdrop. I was head of a segment. My team created a dome from cardboard, painted it black and placed it in a dark environment. Stars and constellations were presented using a projector."),
       ("Calligraphy", "I wrote Qur'anic ayat in large Arabic calligraphy on black chart paper using gold paint. The writing became a major visual attraction because it shone in the dark."),
       ("Recognition", "I received the sharaf of representing the project before His Holiness. My calligraphy was praised by Mukassir-o-Dawat-il-Haq Syedi Malekul Ashtar BS Shujauddin.")],
      ["Arabic calligraphy", "Painting", "Decoration"],
      learned="Leadership, creative problem-solving and teamwork.", pos=5),
    P("learning-thuluth", "Learning Thuluth", "Khat", "", False,
      "A two-month Khat course from Misr focused on Thuluth, with personal checking by an experienced Ustaaz.",
      [("Course", "Two-month Khat course from Misr"), ("Focus", "Thuluth"), ("Feedback", "Personal checking by the Ustaaz")],
      [("Overview", "A two-month Khat course from Misr with a detailed study of Thuluth."),
       ("Learning with an Ustaaz", "The Ustaaz had more than 45 years of experience. He checked my work personally, and his comments and appreciation were a big part of the learning."),
       ("Beyond technique", "The course had philosophical and conceptual dimensions as well as technical ones. For me, Khat is both a technical discipline and an intellectual one.")],
      ["Thuluth", "Personal correction", "Study and practice"], pos=6),
]

JOURNEY_ROWS = [
    # slug, period, title, short, story, points, areas, closing
    ("mumbai", "Early years", "Mumbai: Where It Began", "Born in Mumbai, with pre-primary education at a convent school.", "I was born in Mumbai and attended a convent school for pre-primary education.", [], [], ""),
    ("indore", "Childhood", "Indore: Growing Up", "Grew up in Indore and studied at MSB Educational Institute until Grade 9.", "I was brought up in Indore. I studied at MSB Educational Institute until Grade 9.", [], [], ""),
    ("aljamea-surat", "About four years", "Aljamea Surat: A New Chapter", "Joined after the first two months of Grade 9. Four years of education and personal growth.", "After the first two months of Grade 9, I joined Aljamea-tus-Saifiyah Surat and studied there for about four years. My studies included Kutub ud Da'wat, Deeni subjects and Uloom Kawniyah, the exact sciences in light of Al-Quran.\n\nI had been shy and introverted. Larger groups, new people, communication and responsibility slowly became part of everyday life. There were days when concepts felt hard while classmates seemed to grasp them instantly, and because of my shyness, asking basic questions felt difficult. Comfortable friendships later helped me ask, and clarify the fundamentals.\n\nThat became an important lesson: asking questions is part of learning, not a sign of weakness.", [], [], ""),
    ("online-first-year", "First year", "Online First Year: Learning Differently", "Pandemic-era online education, and a few discoveries.", "My first year at Aljamea was online because of the pandemic. Learning from home became a period of discovery.", ["Arabic typing", "Art", "Sketching", "Independent learning"], [], ""),
    ("aljamea-marol", "Later years", "Aljamea Marol: Another Chapter", "Continued education and grew in confidence and communication.", "I continued my education at the Aljamea-tus-Saifiyah Marol branch. It was another stage of education, communication, social confidence, responsibility and personal growth.", [], [], ""),
    ("art", "Ongoing", "Art: From Small Beginnings", "From an A5 sunset painting to larger projects.", "Art began around Standard 4 with a small A5 sunset painting made in a painting class. My teacher appreciated it, and that small moment sparked a longer journey.\n\nIt grew gradually, not all at once.", ["Sketching", "Painting", "Large canvases", "Arabic handwriting", "Arabic calligraphy", "Maaraz decoration", "Large-scale creative work", "Conceptual artwork"], [], ""),
    ("khat", "Ongoing", "Khat: Discipline Through Form", "Arabic calligraphy through study and practice.", "A two-month Khat course from Misr gave me a detailed study of Thuluth. The Ustaaz, who had more than 45 years of experience, checked my work personally and offered comments and appreciation.\n\nThe course had philosophical and conceptual dimensions too. For me, Khat is both a technical discipline and an intellectual one.", [], [], ""),
    ("creating-and-leading", "Projects", "Creating & Leading", "Four major creative projects, each with its own lesson.", "These projects taught me patience, collaboration, harmony of ideas and leadership.", ["Planetarium Maaraz", "Darajah Haadi Ashara backdrop", "Maaraz Ilmi 1447H", "Zareeh Mubarak"], [], ""),
    ("bcom", "Now", "B.Com", "B.Com at Burhani College, with interests widening.", "I am pursuing B.Com at Burhani College. My interests are widening toward business, entrepreneurship, communication and technology.", ["Business", "Entrepreneurship", "Communication", "Technology"], [], ""),
    ("technology-and-ai", "Now", "Technology & AI", "Learning to build with Python, Django, web development and AI.", "I am learning to build. Python, Django, web development and AI are areas I am exploring and experimenting with, not areas I have mastered. This website is itself one of my learning projects, built with AI assistance.", ["Python", "Django", "Web development", "AI"], [], ""),
    ("today", "Today", "Today", "Creative, intellectual, technical and entrepreneurial.", "Four areas of one identity, all still growing.", [], [["Creative", "Art, Khat and design"], ["Intellectual", "Learning, psychology and knowledge"], ["Technical", "Python, Django and AI, all still being learned"], ["Entrepreneurial", "Business ideas and digital projects"]], ""),
    ("whats-next", "Next", "What's Next", "Deeper Khat, Tazheeb, technology, entrepreneurship and more.", "Where I want to go from here:", ["Deeper Khat", "Tazheeb", "AI and technology", "Entrepreneurship", "Creative projects", "Continuous learning"], [], "The journey continues."),
]

ACH_ROWS = [
    ("Artistic", "Two-month Khat course (Thuluth)", "Studied Thuluth in detail on a two-month Khat course from Misr, with personal checking, comments and appreciation from an Ustaaz of more than 45 years of experience.", "learning-thuluth"),
    ("Certifications", "CorelDRAW Certification", "A certification in CorelDRAW.", ""),
    ("Sports", "District-level Roll Ball", "Played Roll Ball at district level.", ""),
    ("Sports", "Captain, Roll Ball team", "Captained the team.", ""),
    ("Leadership", "Head of the Decoration Team, Maaraz Ilmi 1447H", "Led the Decoration Team, wrote the Maaraz name and main charts, built a painted 3D model of Yemen, and gave a speech.", "maaraz-ilmi-1447h"),
    ("Leadership", "Head of a segment, Planetarium Maaraz", "Led a segment at Aljamea Surat: a cardboard dome, a dark environment, projected stars and gold calligraphy.", "planetarium-maaraz"),
    ("Presentations", "Presented the Darajah Haadi Ashara Backdrop", "Our duo backdrop was presented before His Holiness Syedna Mufaddal Saifuddin TUS.", "darajah-haadi-ashara-backdrop"),
    ("Recognition", "Calligraphy praised, Planetarium Maaraz", "Had the sharaf of representing the project before His Holiness, and my calligraphy was praised by Mukassir-o-Dawat-il-Haq Syedi Malekul Ashtar BS Shujauddin.", "planetarium-maaraz"),
]

POSTS = [
    ("learning-khat", "Learning Khat", "Khat", "Patience, practice and perspective.", "learning-thuluth"),
    ("from-shyness-to-expression", "From Shyness to Expression", "Reflections", "Communication and personal growth.", "aljamea-surat"),
    ("from-an-a5-sunset-to-large-scale-art", "From an A5 Sunset to Large-Scale Art", "Reflections", "The evolution of creativity.", "art, darajah-haadi-ashara-backdrop, zareeh-mubarak"),
    ("learning-to-build-with-ai", "Learning to Build with AI", "AI", "AI, Python, Django and technology learning.", "technology-and-ai"),
    ("learning-to-think-like-a-builder", "Learning to Think Like a Builder", "Business", "B.Com, business and entrepreneurship.", "bcom"),
]

def seed_items():
    out = list(PROJECTS)
    for i, (slug, period, title, short, story, points, areas, closing) in enumerate(JOURNEY_ROWS):
        out.append(dict(kind="journey", slug=slug, title=title, pos=i + 1,
                        data=dict(period=period, short=short, story=story, image="", points=points, areas=areas, closing=closing)))
    for i, (cat, title, details, proj) in enumerate(ACH_ROWS):
        out.append(dict(kind="achievement", slug=f"a{i+1}", title=title, pos=i + 1,
                        data=dict(cat=cat, details=details, project=proj, learned="", recognition="", image="")))
    for i, (slug, title, cat, excerpt, rel) in enumerate(POSTS):
        out.append(dict(kind="post", slug=slug, title=title, pos=i,
                        data=dict(category=cat, excerpt=excerpt, cover="", body="", soon=True, related=rel, date="")))
    return out

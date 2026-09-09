import sqlite3

db = "computer_education.db"

questions = [
("Computer Fundamentals","कंप्यूटर का मस्तिष्क किसे कहा जाता है?","CPU","Monitor","Keyboard","Mouse","CPU","Easy","Computer Basics","Hardware"),
("Computer Fundamentals","RAM का पूरा नाम क्या है?","Read Access Memory","Random Access Memory","Run Access Memory","Rapid Access Memory","Random Access Memory","Easy","Computer Basics","Memory"),
("Computer Fundamentals","कंप्यूटर में डेटा को स्थायी रूप से रखने के लिए सामान्यतः किसका उपयोग होता है?","RAM","Cache","Hard Disk/SSD","Register","Hard Disk/SSD","Easy","Storage","Hardware"),
("Computer Fundamentals","इनमें से कौन-सा input device है?","Monitor","Printer","Speaker","Keyboard","Keyboard","Easy","Input Devices","Hardware"),
("Computer Fundamentals","1 Byte में कितने bits होते हैं?","4","8","16","32","8","Easy","Data Units","Basics"),
("Computer Fundamentals","कंप्यूटर की binary language में कौन-से अंक होते हैं?","1 और 2","2 और 3","0 और 1","5 और 6","0 और 1","Easy","Number System","Basics"),
("Computer Fundamentals","Operating System का मुख्य कार्य क्या है?","केवल typing करना","Hardware और software resources को manage करना","केवल internet चलाना","केवल games चलाना","Hardware और software resources को manage करना","Medium","Operating System","Software"),
("Computer Fundamentals","इनमें से कौन-सा output device है?","Mouse","Scanner","Keyboard","Monitor","Monitor","Easy","Output Devices","Hardware"),
("Computer Fundamentals","CPU में calculation और logical operations मुख्यतः कौन करता है?","ALU","RAM","SSD","BIOS","ALU","Medium","CPU","Hardware"),
("Computer Fundamentals","URL का पूरा नाम क्या है?","Uniform Resource Locator","Universal Record Link","User Resource Location","Uniform Routing Link","Uniform Resource Locator","Medium","Internet","Networking"),

("MS Office","MS Word मुख्य रूप से किस काम के लिए प्रयोग होता है?","Document बनाने और edit करने के लिए","Video editing के लिए","Operating system बनाने के लिए","Database server चलाने के लिए","Document बनाने और edit करने के लिए","Easy","MS Word","Office"),
("MS Office","MS Excel में formula सामान्यतः किस symbol से शुरू होता है?","#","@","=","&","=","Easy","MS Excel","Spreadsheet"),
("MS Office","Excel में columns को सामान्यतः किससे दर्शाया जाता है?","Numbers","Letters","Symbols only","Colors","Letters","Easy","MS Excel","Spreadsheet"),
("MS Office","PowerPoint का उपयोग मुख्यतः किसके लिए होता है?","Presentation बनाने के लिए","Antivirus चलाने के लिए","Programming compiler बनाने के लिए","File compression के लिए","Presentation बनाने के लिए","Easy","MS PowerPoint","Presentation"),
("MS Office","MS Word में text को bold करने की shortcut key क्या है?","Ctrl+B","Ctrl+P","Ctrl+L","Ctrl+K","Ctrl+B","Easy","MS Word","Shortcut"),
("MS Office","Excel में एक cell किससे पहचाना जाता है?","केवल row number से","केवल column letter से","Column letter और row number से","Sheet name से","Column letter और row number से","Medium","MS Excel","Spreadsheet"),
("MS Office","PowerPoint में नई slide जोड़ने की सामान्य shortcut key क्या है?","Ctrl+N","Ctrl+M","Ctrl+S","Ctrl+E","Ctrl+M","Medium","MS PowerPoint","Shortcut"),
("MS Office","MS Word में document save करने की shortcut key क्या है?","Ctrl+S","Ctrl+D","Ctrl+R","Ctrl+T","Ctrl+S","Easy","MS Word","Shortcut"),
("MS Office","Excel में SUM function का उपयोग किसके लिए होता है?","योग करने के लिए","Text बदलने के लिए","Chart हटाने के लिए","File बंद करने के लिए","योग करने के लिए","Easy","MS Excel","Functions"),
("MS Office","PowerPoint में slide show शुरू करने के लिए सामान्यतः कौन-सी key उपयोग होती है?","F1","F3","F5","F12","F5","Easy","MS PowerPoint","Presentation"),

("Python Programming","Python में list किस bracket से लिखी जाती है?","{}","[]","()","<>","[]","Easy","Python Basics","Data Types"),
("Python Programming","Python में comment लिखने के लिए सामान्यतः कौन-सा symbol उपयोग होता है?","//","#","<!-- -->","%%","#","Easy","Python Basics","Syntax"),
("Python Programming","Python में output दिखाने के लिए कौन-सा function उपयोग होता है?","display()","show()","print()","output()","print()","Easy","Python Basics","Functions"),
("Python Programming","Python में integer किस प्रकार का data type है?","str","float","int","list","int","Easy","Data Types","Python"),
("Python Programming","Python में condition check करने के लिए कौन-सा keyword उपयोग होता है?","if","check","condition","when","if","Easy","Control Flow","Python"),
("Python Programming","Python में function बनाने के लिए कौन-सा keyword उपयोग होता है?","function","def","fun","create","def","Easy","Functions","Python"),
("Python Programming","Python में dictionary किस brackets में लिखी जाती है?","[]","()","{}","<>","{}","Easy","Data Structures","Python"),
("Python Programming","Python में कौन-सा operator exponentiation के लिए उपयोग होता है?","^","//","**","%%","**","Medium","Operators","Python"),
("Python Programming","Python में string को किस quotes में लिखा जा सकता है?","केवल double quotes","केवल single quotes","Single या double quotes दोनों","केवल brackets","Single या double quotes दोनों","Easy","Strings","Python"),
("Python Programming","Python में loop को जल्दी रोकने के लिए कौन-सा keyword उपयोग होता है?","stop","exit","break","close","break","Medium","Loops","Python"),

("Web Development","HTML का पूरा नाम क्या है?","HyperText Markup Language","HighText Machine Language","Hyper Transfer Mark Language","Home Tool Markup Language","HyperText Markup Language","Easy","HTML","Web"),
("Web Development","HTML में सबसे बड़ा heading tag कौन-सा है?","<h6>","<h3>","<h1>","<head>","<h1>","Easy","HTML","Web"),
("Web Development","CSS का उपयोग मुख्यतः किसके लिए किया जाता है?","Web page की styling के लिए","Database बनाने के लिए","Server hardware manage करने के लिए","Email भेजने के लिए","Web page की styling के लिए","Easy","CSS","Web"),
("Web Development","HTML में hyperlink बनाने के लिए कौन-सा tag उपयोग होता है?","<link>","<a>","<url>","<href>","<a>","Easy","HTML","Web"),
("Web Development","JavaScript मुख्यतः किसके लिए प्रयोग की जाती है?","Web pages में behavior और interactivity के लिए","केवल images store करने के लिए","केवल operating system बनाने के लिए","केवल printing के लिए","Web pages में behavior और interactivity के लिए","Medium","JavaScript","Web"),
("Web Development","CSS में text का रंग बदलने के लिए कौन-सी property उपयोग होती है?","font-color","text-color","color","foreground","color","Easy","CSS","Web"),
("Web Development","HTML में image जोड़ने के लिए कौन-सा tag उपयोग होता है?","<image>","<img>","<pic>","<src>","<img>","Easy","HTML","Web"),
("Web Development","CSS में background का रंग बदलने के लिए कौन-सी property उपयोग होती है?","bg-color","background-color","back-color","color-background","background-color","Easy","CSS","Web"),
("Web Development","Flask किस programming language का web framework है?","Java","Python","C++","PHP","Python","Medium","Flask","Web"),
("Web Development","HTTP का पूरा नाम क्या है?","HyperText Transfer Protocol","High Transfer Text Program","Hyperlink Transfer Protocol","HyperText Transmission Program","HyperText Transfer Protocol","Medium","Web Basics","Networking")
]

conn = sqlite3.connect(db)
cur = conn.cursor()

cur.executemany("""
INSERT INTO online_questions
(subject, question, option_a, option_b, option_c, option_d,
 correct_answer, difficulty, source, category)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", questions)

conn.commit()

print("QUESTIONS ADDED:", len(questions))
print("TOTAL QUESTIONS:", cur.execute(
    "SELECT COUNT(*) FROM online_questions"
).fetchone()[0])

conn.close()

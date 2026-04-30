from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import date

app = Flask(__name__)
CORS(app)

# Database file path
DATABASE = 'college_portal.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Create tables and insert sample data"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create Events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Events (
            Event_ID TEXT PRIMARY KEY,
            Event_Name TEXT,
            Department TEXT,
            Category TEXT,
            Event_Type TEXT,
            Venue TEXT,
            Event_Date TEXT
        )
    ''')
    
    # Create Participants table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Participants (
            Participant_ID TEXT PRIMARY KEY,
            Name TEXT,
            Type TEXT,
            Department TEXT,
            Year INTEGER,
            College_Name TEXT
        )
    ''')
    
    # Create Registrations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Registrations (
            Reg_ID TEXT PRIMARY KEY,
            Event_ID TEXT,
            Participant_ID TEXT,
            Registration_Date TEXT,
            FOREIGN KEY (Event_ID) REFERENCES Events(Event_ID),
            FOREIGN KEY (Participant_ID) REFERENCES Participants(Participant_ID)
        )
    ''')
    
    # Create Results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Results (
            Result_ID TEXT PRIMARY KEY,
            Event_ID TEXT,
            Participant_ID TEXT,
            Position TEXT,
            Score REAL,
            FOREIGN KEY (Event_ID) REFERENCES Events(Event_ID),
            FOREIGN KEY (Participant_ID) REFERENCES Participants(Participant_ID)
        )
    ''')
    
    # Create Feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Feedback (
            Feedback_ID TEXT PRIMARY KEY,
            Event_ID TEXT,
            Participant_ID TEXT,
            Rating REAL,
            Comments TEXT,
            FOREIGN KEY (Event_ID) REFERENCES Events(Event_ID),
            FOREIGN KEY (Participant_ID) REFERENCES Participants(Participant_ID)
        )
    ''')
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM Events")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("📝 Inserting sample data...")
        
        # Insert Events
        events = [
            ('E001','Coding Contest','CSE','Technical','Competition','Room 101','2026-04-25'),
            ('E002','Hackathon','ISE','Technical','Competition','Auditorium','2026-04-26'),
            ('E003','Robotics Workshop','ECE','Technical','Non-Competition','Lab 3','2026-04-27'),
            ('E004','Cultural Fest','All','Cultural','Non-Competition','Ground','2026-04-28'),
            ('E005','AI Seminar','CSE','Technical','Non-Competition','Room 202','2026-04-29'),
            ('E006','Gaming Tournament','ISE','Technical','Competition','Room 105','2026-04-30'),
            ('E007','Dance Competition','All','Cultural','Competition','Auditorium','2026-05-01'),
            ('E008','Startup Talk','MBA','Business','Non-Competition','Seminar Hall','2026-05-02'),
            ('E009','Photography Contest','Media','Creative','Competition','Campus','2026-05-03'),
            ('E010','Sports Meet','All','Sports','Competition','Ground','2026-05-04')
        ]
        cursor.executemany('INSERT INTO Events VALUES (?,?,?,?,?,?,?)', events)
        
        # Insert Participants (Internal)
        participants = [
            ('P001','Amit','Internal','CSE',1,None),
            ('P002','Sneha','Internal','ISE',2,None),
            ('P003','Rahul','Internal','ECE',3,None),
            ('P004','Pooja','Internal','CSE',4,None),
            ('P005','Kiran','Internal','ME',2,None),
            ('P006','Ravi','Internal','CSE',1,None),
            ('P007','Anjali','Internal','ISE',3,None),
            ('P008','Manoj','Internal','ECE',2,None),
            ('P009','Nisha','Internal','CSE',4,None),
            ('P010','Arjun','Internal','ME',1,None),
            ('P011','Divya','Internal','CSE',2,None),
            ('P012','Varun','Internal','ISE',3,None),
            ('P013','Sita','Internal','ECE',1,None),
            ('P014','Ramesh','Internal','CSE',4,None),
            ('P015','Neha','Internal','ME',2,None),
            ('P016','Akash','Internal','CSE',3,None),
            ('P017','Priya','Internal','ISE',1,None),
            ('P018','Vijay','Internal','ECE',4,None),
            ('P019','Deepa','Internal','CSE',2,None),
            ('P020','Karthik','Internal','ME',3,None),
            ('P021','Swathi','Internal','CSE',1,None),
            ('P022','Rohit','Internal','ISE',2,None),
            ('P023','Lavanya','Internal','ECE',3,None),
            ('P024','Harsha','Internal','CSE',4,None),
            ('P025','Tejas','Internal','ME',2,None)
        ]
        cursor.executemany('INSERT INTO Participants VALUES (?,?,?,?,?,?)', participants)
        
        # Insert External Participants
        external = [
            ('P026','Rohit','External',None,None,'ABC College'),
            ('P027','Neha','External',None,None,'XYZ University'),
            ('P028','Arjun','External',None,None,'PES College'),
            ('P029','Divya','External',None,None,'RV College'),
            ('P030','Varun','External',None,None,'MSRIT'),
            ('P031','Kavya','External',None,None,'BMS College'),
            ('P032','Tarun','External',None,None,'Dayananda Sagar'),
            ('P033','Megha','External',None,None,'SJCE'),
            ('P034','Omkar','External',None,None,'NITK'),
            ('P035','Isha','External',None,None,'MIT Manipal'),
            ('P036','Dev','External',None,None,'Christ University'),
            ('P037','Ritu','External',None,None,'Jain University'),
            ('P038','Ajay','External',None,None,'VTU'),
            ('P039','Maya','External',None,None,'Reva University'),
            ('P040','Anil','External',None,None,'Alliance University'),
            ('P041','Preeti','External',None,None,'New Horizon'),
            ('P042','Sanjay','External',None,None,'Oxford College'),
            ('P043','Rekha','External',None,None,'CMR College'),
            ('P044','Madhu','External',None,None,'Acharya Institute'),
            ('P045','Abhi','External',None,None,'KLE College'),
            ('P046','Meena','External',None,None,'JSS College'),
            ('P047','Sunil','External',None,None,'NMAMIT'),
            ('P048','Radha','External',None,None,'VVCE'),
            ('P049','Pavan','External',None,None,'SIT Tumkur'),
            ('P050','Shreya','External',None,None,'BNMIT')
        ]
        cursor.executemany('INSERT INTO Participants VALUES (?,?,?,?,?,?)', external)
        
        # Insert Registrations
        registrations = [
            ('R001','E001','P001','2026-04-20'),
            ('R002','E001','P006','2026-04-20'),
            ('R003','E001','P011','2026-04-21'),
            ('R004','E001','P026','2026-04-21'),
            ('R005','E001','P031','2026-04-21'),
            ('R006','E002','P002','2026-04-20'),
            ('R007','E002','P007','2026-04-20'),
            ('R008','E002','P012','2026-04-21'),
            ('R009','E002','P027','2026-04-21'),
            ('R010','E002','P032','2026-04-21'),
            ('R011','E003','P003','2026-04-22'),
            ('R012','E003','P008','2026-04-22'),
            ('R013','E003','P013','2026-04-22'),
            ('R014','E003','P028','2026-04-22'),
            ('R015','E003','P033','2026-04-22'),
            ('R016','E004','P004','2026-04-23'),
            ('R017','E004','P009','2026-04-23'),
            ('R018','E004','P014','2026-04-23'),
            ('R019','E004','P029','2026-04-23'),
            ('R020','E004','P034','2026-04-23'),
            ('R021','E005','P005','2026-04-24'),
            ('R022','E005','P010','2026-04-24'),
            ('R023','E005','P015','2026-04-24'),
            ('R024','E005','P030','2026-04-24'),
            ('R025','E005','P035','2026-04-24'),
            ('R026','E006','P016','2026-04-20'),
            ('R027','E006','P017','2026-04-20'),
            ('R028','E006','P018','2026-04-21'),
            ('R029','E006','P036','2026-04-21'),
            ('R030','E006','P041','2026-04-21'),
            ('R031','E007','P019','2026-04-22'),
            ('R032','E007','P020','2026-04-22'),
            ('R033','E007','P021','2026-04-22'),
            ('R034','E007','P037','2026-04-22'),
            ('R035','E007','P042','2026-04-22'),
            ('R036','E008','P022','2026-04-23'),
            ('R037','E008','P023','2026-04-23'),
            ('R038','E008','P024','2026-04-23'),
            ('R039','E008','P038','2026-04-23'),
            ('R040','E008','P043','2026-04-23'),
            ('R041','E009','P025','2026-04-24'),
            ('R042','E009','P001','2026-04-24'),
            ('R043','E009','P006','2026-04-24'),
            ('R044','E009','P039','2026-04-24'),
            ('R045','E009','P044','2026-04-24'),
            ('R046','E010','P002','2026-04-24'),
            ('R047','E010','P007','2026-04-24'),
            ('R048','E010','P012','2026-04-24'),
            ('R049','E010','P040','2026-04-24'),
            ('R050','E010','P045','2026-04-24')
        ]
        cursor.executemany('INSERT INTO Registrations VALUES (?,?,?,?)', registrations)
        
        # Insert Results
        results = [
            ('RES01','E001','P001','Winner',95),
            ('RES02','E001','P006','Runner-up',90),
            ('RES03','E001','P011','2nd Runner-up',85),
            ('RES04','E002','P002','Winner',98),
            ('RES05','E002','P007','Runner-up',92),
            ('RES06','E002','P012','2nd Runner-up',88),
            ('RES07','E006','P016','Winner',89),
            ('RES08','E006','P017','Runner-up',85),
            ('RES09','E006','P018','2nd Runner-up',80),
            ('RES10','E007','P019','Winner',96),
            ('RES11','E007','P020','Runner-up',91),
            ('RES12','E007','P021','2nd Runner-up',87),
            ('RES13','E009','P025','Winner',93),
            ('RES14','E009','P001','Runner-up',89),
            ('RES15','E009','P006','2nd Runner-up',84),
            ('RES16','E010','P002','Winner',97),
            ('RES17','E010','P007','Runner-up',92),
            ('RES18','E010','P012','2nd Runner-up',88)
        ]
        cursor.executemany('INSERT INTO Results VALUES (?,?,?,?,?)', results)
        
        # Insert Feedback
        feedback = [
            ('F001','E001','P001',4.5,'Excellent event'),
            ('F002','E002','P002',4.2,'Very engaging'),
            ('F003','E003','P003',4.0,'Informative'),
            ('F004','E004','P004',4.8,'Loved it'),
            ('F005','E005','P005',4.3,'Great seminar'),
            ('F006','E006','P016',3.9,'Fun event'),
            ('F007','E007','P019',4.6,'Amazing performance'),
            ('F008','E008','P022',4.4,'Motivating'),
            ('F009','E009','P025',4.1,'Creative event'),
            ('F010','E010','P002',4.7,'Well organized')
        ]
        cursor.executemany('INSERT INTO Feedback VALUES (?,?,?,?,?)', feedback)
        
        conn.commit()
        print("✅ Sample data inserted successfully!")
        print("   - 10 Events")
        print("   - 50 Participants (25 Internal, 25 External)")
        print("   - 50 Registrations")
        print("   - 18 Results")
        print("   - 10 Feedback entries")
    
    conn.close()

# Initialize database on startup
init_database()

# Page routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events')
def events_page():
    return render_template('events.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/analytics')
def analytics_page():
    return render_template('analytics.html')

# API Routes
@app.route('/api/stats')
def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM Events")
        total_events = cursor.fetchone()[0]
        
        # Count unique participants who actually registered
        cursor.execute("SELECT COUNT(DISTINCT Participant_ID) FROM Registrations")
        total_participants = cursor.fetchone()[0]
        
        # Count internal vs external from REGISTRATIONS (not Participants table)
        cursor.execute("""
            SELECT 
                p.Type,
                COUNT(DISTINCT p.Participant_ID) as count
            FROM Participants p
            JOIN Registrations r ON p.Participant_ID = r.Participant_ID
            GROUP BY p.Type
        """)
        type_rows = cursor.fetchall()
        type_counts = {row[0]: row[1] for row in type_rows}
        
        cursor.execute("SELECT Department, COUNT(*) FROM Events GROUP BY Department")
        dept_rows = cursor.fetchall()
        dept_events = {row[0]: row[1] for row in dept_rows}
        
        return jsonify({
            'total_events': total_events,
            'total_participants': total_participants,
            'internal_count': type_counts.get('Internal', 0),
            'external_count': type_counts.get('External', 0),
            'dept_events': dept_events
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/events')
def get_events():
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT e.*, COUNT(DISTINCT r.Participant_ID) as participant_count
            FROM Events e
            LEFT JOIN Registrations r ON e.Event_ID = r.Event_ID
            GROUP BY e.Event_ID
            ORDER BY e.Event_Date
        """)
        rows = cursor.fetchall()
        events = [dict(row) for row in rows]
        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/events', methods=['POST'])
def add_event():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM Events")
        count = cursor.fetchone()[0] + 1
        event_id = f"E{count:03d}"
        
        cursor.execute("""
            INSERT INTO Events (Event_ID, Event_Name, Department, Category, Event_Type, Venue, Event_Date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (event_id, data['event_name'], data['department'], 
              data['category'], data['event_type'], data['venue'], data['event_date']))
        
        conn.commit()
        return jsonify({'message': 'Event added', 'event_id': event_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/winners')
def get_winners():
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT e.Event_Name, p.Name, r.Position, r.Score
            FROM Results r
            JOIN Events e ON r.Event_ID = e.Event_ID
            JOIN Participants p ON r.Participant_ID = p.Participant_ID
            WHERE r.Position = 'Winner'
            ORDER BY r.Score DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
        winners = [{'event_name': row[0], 'name': row[1], 'position': row[2], 'score': row[3]} for row in rows]
        return jsonify(winners)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/event-participants')
def get_event_participants():
    """Get participants per event"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                e.Event_Name,
                COUNT(DISTINCT r.Participant_ID) as participant_count
            FROM Events e
            LEFT JOIN Registrations r ON e.Event_ID = r.Event_ID
            GROUP BY e.Event_ID
            ORDER BY participant_count DESC
        """)
        rows = cursor.fetchall()
        results = [{'event_name': row[0], 'participants': row[1]} for row in rows]
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/average-scores')
def get_average_scores():
    """Get average score per event for competitions"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                e.Event_Name,
                ROUND(AVG(r.Score), 2) as avg_score,
                COUNT(r.Result_ID) as total_results,
                MAX(r.Score) as highest_score,
                MIN(r.Score) as lowest_score
            FROM Events e
            JOIN Results r ON e.Event_ID = r.Event_ID
            WHERE r.Score IS NOT NULL
            GROUP BY e.Event_ID
            ORDER BY avg_score DESC
        """)
        rows = cursor.fetchall()
        results = [{
            'event_name': row[0],
            'avg_score': row[1],
            'total_results': row[2],
            'highest_score': row[3],
            'lowest_score': row[4]
        } for row in rows]
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/ratings-summary')
def get_ratings_summary():
    """Get detailed feedback ratings"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                e.Event_Name,
                ROUND(AVG(f.Rating), 2) as avg_rating,
                COUNT(f.Feedback_ID) as total_feedback,
                MAX(f.Rating) as highest_rating,
                MIN(f.Rating) as lowest_rating
            FROM Events e
            JOIN Feedback f ON e.Event_ID = f.Event_ID
            GROUP BY e.Event_ID
            ORDER BY avg_rating DESC
        """)
        rows = cursor.fetchall()
        results = [{
            'event_name': row[0],
            'avg_rating': row[1],
            'total_feedback': row[2],
            'highest_rating': row[3],
            'lowest_rating': row[4]
        } for row in rows]
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/top-performers')
def top_performers():
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                p.Name,
                COALESCE(p.Department, 'External') as Department,
                COUNT(r.Result_ID) as wins,
                ROUND(AVG(r.Score), 2) as avg_score
            FROM Results r
            JOIN Participants p ON r.Participant_ID = p.Participant_ID
            WHERE r.Position = 'Winner'
            GROUP BY p.Participant_ID, p.Name, p.Department
            ORDER BY wins DESC, avg_score DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
        performers = [{'name': row[0], 'department': row[1], 'wins': row[2], 'avg_score': row[3]} for row in rows]
        return jsonify(performers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/register', methods=['POST'])
def register_participant():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Check if participant exists
        cursor.execute("SELECT Participant_ID FROM Participants WHERE Participant_ID = ?", 
                      (data['participant_id'],))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO Participants (Participant_ID, Name, Type, Department, Year, College_Name)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (data['participant_id'], data['name'], data['type'],
                  data.get('department'), data.get('year'), data.get('college_name')))
        
        # Generate Reg_ID
        cursor.execute("SELECT COUNT(*) FROM Registrations")
        count = cursor.fetchone()[0] + 1
        reg_id = f"R{count:03d}"
        
        cursor.execute("""
            INSERT INTO Registrations (Reg_ID, Event_ID, Participant_ID, Registration_Date)
            VALUES (?, ?, ?, date('now'))
        """, (reg_id, data['event_id'], data['participant_id']))
        
        conn.commit()
        return jsonify({'message': 'Registration successful', 'reg_id': reg_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("🎓 College Event Portal Starting...")
    print("=" * 60)
    print("📍 Open your browser and go to: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, port=5000)
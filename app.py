from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

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
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        cur.execute("SELECT COUNT(*) FROM Events")
        total_events = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(DISTINCT Participant_ID) FROM Registrations")
        total_participants = cur.fetchone()[0]
        
        cur.execute("SELECT Type, COUNT(*) FROM Participants GROUP BY Type")
        type_counts = {row[0]: row[1] for row in cur.fetchall()}
        
        cur.execute("SELECT Department, COUNT(*) FROM Events GROUP BY Department")
        dept_events = {row[0]: row[1] for row in cur.fetchall()}
        
        # Calculate average participants per event
        cur.execute("""
            SELECT AVG(participant_count) FROM (
                SELECT COUNT(DISTINCT Participant_ID) as participant_count 
                FROM Registrations GROUP BY Event_ID
            ) as counts
        """)
        avg_participants = cur.fetchone()[0] or 0
        
        return jsonify({
            'total_events': total_events,
            'total_participants': total_participants,
            'internal_count': type_counts.get('Internal', 0),
            'external_count': type_counts.get('External', 0),
            'dept_events': dept_events,
            'avg_participants_per_event': round(avg_participants, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/events')
def get_events():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        cur.execute("""
            SELECT e.*, COUNT(DISTINCT r.Participant_ID) as participant_count
            FROM Events e
            LEFT JOIN Registrations r ON e.Event_ID = r.Event_ID
            GROUP BY e.Event_ID
            ORDER BY e.Event_Date
        """)
        events = [dict(row) for row in cur.fetchall()]
        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/events', methods=['POST'])
def add_event():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT COUNT(*) FROM Events")
        count = cur.fetchone()[0] + 1
        event_id = f"E{count:03d}"
        
        cur.execute("""
            INSERT INTO Events (Event_ID, Event_Name, Department, Category, Event_Type, Venue, Event_Date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (event_id, data['event_name'], data['department'], 
              data['category'], data['event_type'], data['venue'], data['event_date']))
        
        conn.commit()
        return jsonify({'message': 'Event added', 'event_id': event_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/winners')
def get_winners():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        cur.execute("""
            SELECT e.Event_Name, p.Name, r.Position, r.Score
            FROM Results r
            JOIN Events e ON r.Event_ID = e.Event_ID
            JOIN Participants p ON r.Participant_ID = p.Participant_ID
            WHERE r.Position = 'Winner'
            ORDER BY r.Score DESC
            LIMIT 10
        """)
        winners = [dict(row) for row in cur.fetchall()]
        return jsonify(winners)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/feedback-summary')
def feedback_summary():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        cur.execute("""
            SELECT e.Event_Name, ROUND(AVG(f.Rating), 2) as avg_rating, COUNT(f.Feedback_ID) as feedback_count
            FROM Events e
            JOIN Feedback f ON e.Event_ID = f.Event_ID
            GROUP BY e.Event_Name
            ORDER BY avg_rating DESC
        """)
        feedback = [dict(row) for row in cur.fetchall()]
        return jsonify(feedback)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/top-performers')
def top_performers():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        cur.execute("""
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
        performers = [dict(row) for row in cur.fetchall()]
        return jsonify(performers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/register', methods=['POST'])
def register_participant():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cur = conn.cursor()
    
    try:
        # Check if participant exists
        cur.execute("SELECT Participant_ID FROM Participants WHERE Participant_ID = %s", 
                    (data['participant_id'],))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO Participants (Participant_ID, Name, Type, Department, Year, College_Name)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (data['participant_id'], data['name'], data['type'],
                  data.get('department'), data.get('year'), data.get('college_name')))
        
        # Generate Reg_ID
        cur.execute("SELECT COUNT(*) FROM Registrations")
        count = cur.fetchone()[0] + 1
        reg_id = f"R{count:03d}"
        
        cur.execute("""
            INSERT INTO Registrations (Reg_ID, Event_ID, Participant_ID, Registration_Date)
            VALUES (%s, %s, %s, CURRENT_DATE)
        """, (reg_id, data['event_id'], data['participant_id']))
        
        conn.commit()
        return jsonify({'message': 'Registration successful', 'reg_id': reg_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("🎓 College Event Portal Starting...")
    print("=" * 60)
    print("📍 Open your browser and go to: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, port=5000)
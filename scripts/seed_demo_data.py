"""
seed_demo_data.py — Seeds EIT MongoDB with demo topics and lessons.

Usage:
    cd scripts
    python seed_demo_data.py [--uri mongodb://localhost:27017/] [--db eit_database] [--clear]

Options:
    --uri    MongoDB connection URI (default: from MONGODB_URI env var or localhost)
    --db     Database name (default: eit_database)
    --clear  Drop existing topics and lessons before seeding
"""

import argparse
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# Allow running from project root or scripts/ directory
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
except ImportError:
    print("ERROR: pymongo not installed. Run: pip install pymongo")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / "backend" / ".env")
except ImportError:
    pass


def utcnow():
    return datetime.now(timezone.utc)


TOPICS = [
    {
        "title": "Java Fundamentals",
        "description": "Learn the basics of Java programming: syntax, data types, control flow, and object-oriented concepts.",
        "category": "programming",
        "is_active": True,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    },
    {
        "title": "Object-Oriented Programming",
        "description": "Master OOP principles: encapsulation, inheritance, polymorphism, and abstraction with practical examples.",
        "category": "programming",
        "is_active": True,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    },
    {
        "title": "Data Structures and Algorithms",
        "description": "Explore fundamental data structures (arrays, linked lists, trees, graphs) and algorithms (sorting, searching).",
        "category": "computer_science",
        "is_active": True,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    },
    {
        "title": "SQL and Database Concepts",
        "description": "Learn SQL queries, database design, normalization, and how relational databases work.",
        "category": "databases",
        "is_active": True,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    },
    {
        "title": "Operating Systems",
        "description": "Understand OS concepts: processes, threads, memory management, file systems, and scheduling.",
        "category": "computer_science",
        "is_active": True,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    },
    {
        "title": "Computer Networks",
        "description": "Study networking fundamentals: protocols, TCP/IP, HTTP, DNS, routing, and network security basics.",
        "category": "networking",
        "is_active": True,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    },
]

# Map: topic title -> list of lessons
LESSONS_BY_TOPIC = {
    "Java Fundamentals": [
        {
            "title": "Introduction to Java",
            "description": "What is Java? JVM, JDK, JRE explained. Your first Hello World program.",
            "video_url": "https://www.youtube.com/embed/eIrMbAQSU34",
            "video_type": "youtube",
            "duration_seconds": 600,
            "sequence_number": 1,
            "is_published": True,
        },
        {
            "title": "Variables and Data Types",
            "description": "Primitive types (int, double, boolean, char), String, variable declaration and initialization.",
            "video_url": "https://www.youtube.com/embed/C6WMAfrar3Y",
            "video_type": "youtube",
            "duration_seconds": 720,
            "sequence_number": 2,
            "is_published": True,
        },
        {
            "title": "Control Flow: if, loops",
            "description": "if/else statements, for loops, while loops, do-while, switch statements.",
            "video_url": "https://www.youtube.com/embed/p9DJEObFuiU",
            "video_type": "youtube",
            "duration_seconds": 840,
            "sequence_number": 3,
            "is_published": True,
        },
        {
            "title": "Methods and Functions",
            "description": "Defining methods, parameters, return types, method overloading, and scope.",
            "video_url": "https://www.youtube.com/embed/p9DJEObFuiU",
            "video_type": "youtube",
            "duration_seconds": 780,
            "sequence_number": 4,
            "is_published": True,
        },
    ],
    "Object-Oriented Programming": [
        {
            "title": "Classes and Objects",
            "description": "Defining classes, creating objects, constructors, instance variables, and methods.",
            "video_url": "https://www.youtube.com/embed/pTB0EiLXUC8",
            "video_type": "youtube",
            "duration_seconds": 900,
            "sequence_number": 1,
            "is_published": True,
        },
        {
            "title": "Encapsulation",
            "description": "Access modifiers (public, private, protected), getters and setters, data hiding.",
            "video_url": "https://www.youtube.com/embed/pTB0EiLXUC8",
            "video_type": "youtube",
            "duration_seconds": 660,
            "sequence_number": 2,
            "is_published": True,
        },
        {
            "title": "Inheritance",
            "description": "Extending classes, super keyword, method overriding, is-a relationships.",
            "video_url": "https://www.youtube.com/embed/pTB0EiLXUC8",
            "video_type": "youtube",
            "duration_seconds": 780,
            "sequence_number": 3,
            "is_published": True,
        },
        {
            "title": "Polymorphism and Abstraction",
            "description": "Runtime polymorphism, abstract classes, interfaces, and design principles.",
            "video_url": "https://www.youtube.com/embed/pTB0EiLXUC8",
            "video_type": "youtube",
            "duration_seconds": 900,
            "sequence_number": 4,
            "is_published": True,
        },
    ],
    "Data Structures and Algorithms": [
        {
            "title": "Arrays and ArrayLists",
            "description": "Static arrays vs dynamic lists, indexing, searching, time complexity basics.",
            "video_url": "https://www.youtube.com/embed/eXBa2jK8pO0",
            "video_type": "youtube",
            "duration_seconds": 720,
            "sequence_number": 1,
            "is_published": True,
        },
        {
            "title": "Linked Lists",
            "description": "Singly and doubly linked lists, insertion, deletion, traversal.",
            "video_url": "https://www.youtube.com/embed/eXBa2jK8pO0",
            "video_type": "youtube",
            "duration_seconds": 840,
            "sequence_number": 2,
            "is_published": True,
        },
        {
            "title": "Stacks and Queues",
            "description": "LIFO and FIFO structures, implementation, real-world applications.",
            "video_url": "https://www.youtube.com/embed/eXBa2jK8pO0",
            "video_type": "youtube",
            "duration_seconds": 600,
            "sequence_number": 3,
            "is_published": True,
        },
        {
            "title": "Sorting Algorithms",
            "description": "Bubble sort, selection sort, insertion sort, merge sort, quick sort — complexity analysis.",
            "video_url": "https://www.youtube.com/embed/eXBa2jK8pO0",
            "video_type": "youtube",
            "duration_seconds": 1080,
            "sequence_number": 4,
            "is_published": True,
        },
    ],
    "SQL and Database Concepts": [
        {
            "title": "Introduction to Databases",
            "description": "What is a database? RDBMS vs NoSQL, tables, rows, columns, primary keys.",
            "video_url": "https://www.youtube.com/embed/HXV3zeQKqGY",
            "video_type": "youtube",
            "duration_seconds": 840,
            "sequence_number": 1,
            "is_published": True,
        },
        {
            "title": "SELECT Queries",
            "description": "Basic SELECT, WHERE, ORDER BY, LIMIT, filtering and sorting data.",
            "video_url": "https://www.youtube.com/embed/HXV3zeQKqGY",
            "video_type": "youtube",
            "duration_seconds": 720,
            "sequence_number": 2,
            "is_published": True,
        },
        {
            "title": "JOINs and Relationships",
            "description": "INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN with practical examples.",
            "video_url": "https://www.youtube.com/embed/HXV3zeQKqGY",
            "video_type": "youtube",
            "duration_seconds": 960,
            "sequence_number": 3,
            "is_published": True,
        },
        {
            "title": "Aggregation and GROUP BY",
            "description": "COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING clause.",
            "video_url": "https://www.youtube.com/embed/HXV3zeQKqGY",
            "video_type": "youtube",
            "duration_seconds": 780,
            "sequence_number": 4,
            "is_published": True,
        },
    ],
    "Operating Systems": [
        {
            "title": "What is an Operating System?",
            "description": "OS roles, kernel, user space, system calls, process management overview.",
            "video_url": "https://www.youtube.com/embed/26QPDBe-NB8",
            "video_type": "youtube",
            "duration_seconds": 720,
            "sequence_number": 1,
            "is_published": True,
        },
        {
            "title": "Processes and Threads",
            "description": "Process vs thread, PCB, context switching, multi-threading, concurrency.",
            "video_url": "https://www.youtube.com/embed/26QPDBe-NB8",
            "video_type": "youtube",
            "duration_seconds": 900,
            "sequence_number": 2,
            "is_published": True,
        },
        {
            "title": "Memory Management",
            "description": "Virtual memory, paging, segmentation, TLB, page replacement algorithms.",
            "video_url": "https://www.youtube.com/embed/26QPDBe-NB8",
            "video_type": "youtube",
            "duration_seconds": 1020,
            "sequence_number": 3,
            "is_published": True,
        },
        {
            "title": "File Systems",
            "description": "File organization, directories, inodes, FAT, ext4, NTFS basics.",
            "video_url": "https://www.youtube.com/embed/26QPDBe-NB8",
            "video_type": "youtube",
            "duration_seconds": 840,
            "sequence_number": 4,
            "is_published": True,
        },
    ],
    "Computer Networks": [
        {
            "title": "Network Fundamentals",
            "description": "LAN, WAN, topologies, network devices (routers, switches, hubs), OSI model.",
            "video_url": "https://www.youtube.com/embed/3QhU9jd03a0",
            "video_type": "youtube",
            "duration_seconds": 960,
            "sequence_number": 1,
            "is_published": True,
        },
        {
            "title": "TCP/IP Model",
            "description": "TCP vs UDP, IP addressing, subnetting, CIDR, the four-layer model.",
            "video_url": "https://www.youtube.com/embed/3QhU9jd03a0",
            "video_type": "youtube",
            "duration_seconds": 840,
            "sequence_number": 2,
            "is_published": True,
        },
        {
            "title": "HTTP and DNS",
            "description": "How HTTP works, request/response cycle, status codes, DNS resolution.",
            "video_url": "https://www.youtube.com/embed/3QhU9jd03a0",
            "video_type": "youtube",
            "duration_seconds": 720,
            "sequence_number": 3,
            "is_published": True,
        },
        {
            "title": "Network Security Basics",
            "description": "Firewalls, TLS/SSL, VPN, common attacks (MITM, DDoS), defense strategies.",
            "video_url": "https://www.youtube.com/embed/3QhU9jd03a0",
            "video_type": "youtube",
            "duration_seconds": 900,
            "sequence_number": 4,
            "is_published": True,
        },
    ],
}


def connect_db(uri: str, db_name: str):
    """Connect to MongoDB with a timeout."""
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
        client.admin.command("ping")
        print(f"[OK] Connected to MongoDB at {uri}")
        return client[db_name]
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"[ERROR] Could not connect to MongoDB: {e}")
        print("  Make sure MongoDB is running: mongod")
        sys.exit(1)


def seed(db, clear: bool = False):
    """Seed topics and lessons into MongoDB."""
    if clear:
        print("Clearing existing topics and lessons...")
        db.topics.delete_many({})
        db.lessons.delete_many({})
        print("  [OK] Cleared topics and lessons")

    # Insert topics
    topic_id_map = {}
    topics_inserted = 0
    for topic_data in TOPICS:
        existing = db.topics.find_one({"title": topic_data["title"]})
        if existing:
            topic_id_map[topic_data["title"]] = existing["_id"]
            print(f"  ~ Topic already exists: {topic_data['title']}")
        else:
            result = db.topics.insert_one(topic_data)
            topic_id_map[topic_data["title"]] = result.inserted_id
            topics_inserted += 1
            print(f"  [+] Inserted topic: {topic_data['title']}")

    print(f"\nTopics: {topics_inserted} inserted, {len(TOPICS) - topics_inserted} already existed")

    # Insert lessons
    lessons_inserted = 0
    for topic_title, lessons in LESSONS_BY_TOPIC.items():
        topic_id = topic_id_map.get(topic_title)
        if not topic_id:
            print(f"  ! Could not find topic ID for: {topic_title}")
            continue

        for lesson_data in lessons:
            existing = db.lessons.find_one(
                {"topic_id": topic_id, "sequence_number": lesson_data["sequence_number"]}
            )
            if existing:
                print(f"  ~ Lesson already exists: [{topic_title}] {lesson_data['title']}")
                continue

            lesson_doc = {
                **lesson_data,
                "topic_id": topic_id,
                "created_at": utcnow(),
                "updated_at": utcnow(),
            }
            db.lessons.insert_one(lesson_doc)
            lessons_inserted += 1
            print(f"  [+] Inserted lesson: [{topic_title}] {lesson_data['title']}")

    print(f"\nLessons: {lessons_inserted} inserted")
    print(f"\n{'='*50}")
    print("[OK] Seeding complete!")
    print(f"  Topics in DB:  {db.topics.count_documents({})}")
    print(f"  Lessons in DB: {db.lessons.count_documents({})}")


def main():
    parser = argparse.ArgumentParser(description="Seed EIT demo data into MongoDB")
    parser.add_argument(
        "--uri",
        default=os.getenv("MONGODB_URI", "mongodb://localhost:27017/"),
        help="MongoDB connection URI",
    )
    parser.add_argument(
        "--db",
        default=os.getenv("MONGODB_DATABASE", "eit_database"),
        help="Database name",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing topics and lessons before seeding",
    )
    args = parser.parse_args()

    print(f"EIT Demo Data Seeder")
    print(f"  URI: {args.uri}")
    print(f"  DB:  {args.db}")
    print(f"  Clear first: {args.clear}")
    print()

    db = connect_db(args.uri, args.db)
    seed(db, clear=args.clear)


if __name__ == "__main__":
    main()

import mysql.connector
import logging
from data_layer.config import DATABASE_CONFIG

class StudentDao:
    """
    @class StudentDao
    @brief Data Access Object (DAO) class for interacting with the students table in the database.
    
    This class provides methods to perform CRUD (Create, Read, Update, Delete) operations on the students table.
    """

    def __init__(self):
        """
        @brief Constructor for StudentDao.
        
        Initializes the database connection and cursor.
        """
        self.conn = mysql.connector.connect(**DATABASE_CONFIG)
        self.cursor = self.conn.cursor()

    def __del__(self):
        """
        @brief Destructor for StudentDao.
        
        Closes the database cursor and connection when the instance is destroyed.
        """
        self.cursor.close()
        self.conn.close()

    def add_student(self, name, mat_number, email):
        """
        @brief Adds a new student to the students table.
        
        @param name The name of the student.
        @param mat_number The matriculation number of the student.
        @param email The email address of the student.
        """
        self.cursor.execute(
            "INSERT INTO students (name, mat_number, email) VALUES (%s, %s, %s)",
            (name, mat_number, email)
        )
        self.conn.commit()
        logging.info(f"StudentDao::Added student: {name}")

    def get_all_students(self):
        """
        @brief Retrieves all students from the students table.
        
        @return A list of tuples, each representing a student record.
        """
        self.cursor.execute("SELECT * FROM students")
        students = self.cursor.fetchall()
        logging.info("StudentDao::Retrieved all students")
        return students

    def get_all_matriculation_numbers(self):
        """
        @brief Retrieves all matriculation numbers from the students table.
        
        @return A list of matriculation numbers.
        """
        self.cursor.execute("SELECT mat_number FROM students")
        mat_numbers = [number[0] for number in self.cursor.fetchall()]
        logging.info("StudentDao::Retrieved all matriculation numbers")
        return mat_numbers

    def get_student_by_matriculation_number(self, mat_number):
        """
        @brief Retrieves a student by their matriculation number.
        
        @param mat_number The matriculation number of the student.
        @return A tuple containing the student's ID and matriculation number if found.
        """
        self.cursor.execute("SELECT id, mat_number FROM students WHERE mat_number = %s", (mat_number,))
        student = self.cursor.fetchone()
        logging.info(f"StudentDao::Retrieved student by matriculation number: {mat_number}")
        return student

    def get_name_from_nfc_uid(self, nfc_uid):
        """
        @brief Retrieves the student's name associated with the given NFC UID.
        
        @param nfc_uid The NFC UID of the student.
        @return The name of the student if found, otherwise None.
        """
        self.cursor.execute("SELECT name FROM students WHERE nfc_uid = %s", (nfc_uid,))
        student = self.cursor.fetchone()

        if student:
            logging.info(f"StudentDao::Retrieved student name '{student[0]}' from NFC UID {nfc_uid}.")
            return student[0]  # Return the student's name
        else:
            logging.info(f"StudentDao::No student found with NFC UID {nfc_uid}.")
            return None

    def get_matriculation_number_from_nfc_uid(self, nfc_uid):
        """
        @brief Retrieves the matriculation number associated with the given NFC UID.
        
        @param nfc_uid The NFC UID of the student.
        @return The matriculation number if found, otherwise None.
        """
        self.cursor.execute("SELECT mat_number FROM students WHERE nfc_uid = %s", (nfc_uid,))
        result = self.cursor.fetchone()

        if result:
            logging.info(f"StudentDao::Retrieved matriculation number '{result[0]}' for NFC UID {nfc_uid}.")
            return result[0]  # Return the matriculation number
        else:
            logging.info(f"StudentDao::No matriculation number found for NFC UID {nfc_uid}.")
            return None

    def update_student(self, student_id, name=None, mat_number=None, email=None):
        """
        @brief Updates a student's information in the database.
        
        @param student_id The ID of the student to be updated.
        @param name The new name of the student (optional).
        @param mat_number The new matriculation number of the student (optional).
        @param email The new email address of the student (optional).
        """
        query = "UPDATE students SET "
        params = []
        if name:
            query += "name = %s, "
            params.append(name)
        if mat_number:
            query += "mat_number = %s, "
            params.append(mat_number)
        if email:
            query += "email = %s, "
            params.append(email)
        query = query.rstrip(', ')
        query += " WHERE id = %s"
        params.append(student_id)

        self.cursor.execute(query, tuple(params))
        self.conn.commit()
        logging.info(f"StudentDao::Updated student ID: {student_id}")

    def delete_student(self, student_id):
        """
        @brief Deletes a student from the database.
        
        @param student_id The ID of the student to be deleted.
        """
        self.cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        self.conn.commit()
        logging.info(f"StudentDao::Deleted student ID: {student_id}")
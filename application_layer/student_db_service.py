import logging
from data_access_layer.student_dao import StudentDao

class StudentDBService:
    def __init__(self):
        """
        @brief Constructor for StudentDBService.
        """
        self.student_dao = StudentDao()

    def add_student(self, name, mat_number, email):
        """
        @brief Adds a new student to the database.
        @param name The name of the student.
        @param mat_number The matriculation number of the student.
        @param email The email address of the student.
        """
        self.student_dao.add_student(name, mat_number, email)
        logging.info(f"StudentDBService::Added student {name}")

    def get_all_students(self):
        """
        @brief Retrieves all students from the database.
        @return A list of all students.
        """
        students = self.student_dao.get_all_students()
        logging.info("StudentDBService::Retrieved all students")
        return students

    def get_all_matriculation_numbers(self):
        """
        @brief Retrieves all matriculation numbers from the database.
        @return A list of all matriculation numbers.
        """
        mat_numbers = self.student_dao.get_all_matriculation_numbers()
        logging.info("StudentDBService::Retrieved all matriculation numbers")
        return mat_numbers

    def get_name_from_nfc_uid(self, nfc_uid):
        """
        @brief Retrieves the name of a student based on their NFC UID.
        @param nfc_uid The NFC UID of the student.
        @return The name of the student.
        """
        student_name = self.student_dao.get_name_from_nfc_uid(nfc_uid)
        logging.info(f"StudentDBService::Retrieved student name from {nfc_uid}")
        return student_name

    def get_matriculation_number_from_nfc_uid(self, nfc_uid):
        """
        @brief Retrieves the matriculation number of a student based on their NFC UID.
        @param nfc_uid The NFC UID of the student.
        @return The matriculation number of the student.
        """
        mat_number = self.student_dao.get_matriculation_number_from_nfc_uid(nfc_uid)
        logging.info(f"StudentDBService::Retrieved matriculation number of {nfc_uid}")
        return mat_number
        
    def get_id_from_matriculation_number(self, mat_number):
        """
        @brief Retrieves the ID of a student based on their matriculation number.
        @param mat_number The matriculation number of the student.
        @return The ID of the student, or None if not found.
        """
        student = self.student_dao.get_student_by_matriculation_number(mat_number)
        logging.info(f"StudentDBService::Retrieved ID for matriculation number {mat_number}")
        return student[0] if student else None

    def get_name_from_matriculation_number(self, mat_number):
        """
        @brief Retrieves the name of a student based on their matriculation number.
        @param mat_number The matriculation number of the student.
        @return The name of the student.
        """
        name = self.student_dao.get_student_name_by_matriculation_number(mat_number)
        logging.info(f"StudentDBService::Retrieved name for matriculation number {mat_number}")
        return name

    def update_student(self, student_id, name=None, mat_number=None, email=None):
        """
        @brief Updates the details of a student in the database.
        @param student_id The ID of the student to update.
        @param name The new name of the student (optional).
        @param mat_number The new matriculation number of the student (optional).
        @param email The new email address of the student (optional).
        """
        self.student_dao.update_student(student_id, name, mat_number, email)
        logging.info(f"StudentDBService::Updated student ID {student_id}")

    def delete_student(self, student_id):
        """
        @brief Deletes a student from the database.
        @param student_id The ID of the student to delete.
        """
        self.student_dao.delete_student(student_id)
        logging.info(f"StudentDBService::Deleted student ID {student_id}")
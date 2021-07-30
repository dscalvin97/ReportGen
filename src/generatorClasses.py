from operator import le


def listAvg(lst):
    return sum(lst) / len(lst)


class Student:
    def __init__(
        self,
        fname,
        lname,
        dob,
        gender,
        city,
        country,
        grade,
        registration,
        school,
        subject,
        total_marks,
        test_date,
        final_result,
        profile_dir,
        test_round_no,
        test_total,
        total_attempts,
        correct_attempts,
        question_score_category,
        question_details
    ):
        self.fname = fname
        self.lname = lname
        self.dob = dob
        self.gender = gender
        self.city = city
        self.country = country
        self.grade = grade
        self.registration_number = registration
        self.school_name = school
        self.test_subject = subject
        self.total_marks = total_marks
        self.test_date = test_date
        self.final_result = final_result
        self.profile_img = profile_dir
        self.test_round_no = test_round_no
        self.test_total = test_total
        self.total_attempts = total_attempts
        self.correct_attempts = correct_attempts
        self.question_score_category = question_score_category
        self.question_details = question_details

    def get_student_template_var(self):
        return {
            "student_fname": self.fname,
            "student_name": self.fname + " " + self.lname,
            "student_dob": self.dob,
            "student_gender": self.gender,
            "student_address": self.city + ", " + self.country,
            "student_grade": self.grade,
            "student_regid": self.registration_number,
            "school_name": self.school_name,
            "subject_name": self.test_subject,
            "student_total_marks": self.total_marks,
            "student_test_date": self.test_date,
            "student_final_result": self.final_result,
            "student_profile_img": self.profile_img,
            "test_round_no": self.test_round_no,
            "test_total": self.test_total,
            "question_details": list(self.question_details.items())
        }


class TestResults:
    def __init__(self):
        self.subject = ''
        self.student_count = 0
        self.question_count = 0
        self.students = []
        self.q_score_categories = []
        self.q_accuracy_global_avg = []
        self.q_attempt_global_avg_lst = []
        self.q_correct_global_avg_lst = []
        self.q_incorrect_global_avg_lst = []
        self.q_category_global_avg = []

    def update_student_count(self):
        self.student_count = len(self.students)

    def update_global_averages(self):
        # global average for total question attempts in test
        self.q_attempts_global_avg = [x.total_attempts for x in self.students]
        self.q_attempts_global_avg = listAvg(self.q_attempts_global_avg)

        # global average for total correct question attempts in test
        self.q_correct_global_avg = [x.correct_attempts for x in self.students]
        self.q_correct_global_avg = listAvg(self.q_correct_global_avg)

        # global average for total incorrect question attempts in test
        self.q_incorrect_global_avg = [
            x.total_attempts - x.correct_attempts for x in self.students]
        self.q_incorrect_global_avg = listAvg(self.q_incorrect_global_avg)

        # global average accuracy per question
        self.q_accuracy_global_avg = [0 for x in range(self.question_count)]

        # global average accuracy per question score category
        self.q_category_global_avg = [
            0 for x in range(len(self.q_score_categories))]

        # global average for question attempts for each question
        self.q_attempt_global_avg_lst = [
            x / self.student_count for x in self.q_attempt_global_avg_lst]

        # global average for correct question attempts for each question
        self.q_correct_global_avg_lst = [
            x / self.student_count for x in self.q_correct_global_avg_lst
        ]

        # populating q_accuracy_global_avg and q_category_global_avg with total values
        for student in self.students:
            question_scores = []
            for question_idx in range(self.question_count):
                question_scores.append(
                    student.question_details['Q'+str(question_idx+1)][-1])
            self.q_accuracy_global_avg = [
                self.q_accuracy_global_avg[x] + 1 if question_scores[x] > 0 else self.q_accuracy_global_avg[x] for x in range(len(question_scores))]

            for category_idx in range(len(self.q_score_categories)):
                self.q_category_global_avg[category_idx] = \
                    self.q_category_global_avg[category_idx] + \
                    self.q_score_categories[category_idx]

        # updating q_accuracy_global_avg and q_category_global_avg with averaged values
        self.q_accuracy_global_avg = [
            x / self.student_count for x in self.q_accuracy_global_avg]
        self.q_category_global_avg = [
            x / self.student_count for x in self.q_category_global_avg]

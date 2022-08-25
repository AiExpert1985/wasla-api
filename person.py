from location import Location
from utils import *


class Person:

    def __init__(self, person_id, loc, center_coords, name, district, phone):
        self.id = person_id
        self.loc = loc
        self.preferences = []
        self.iterable_preferences = None
        self.center_coords = center_coords
        self.name = str(name)
        self.district = str(district)
        self.phone = str(phone)

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_district(self):
        return self.district

    def get_phone(self):
        return self.phone

    def sorted_by_criterion(self, people, criterion, flipped=False):
        sort_func = getattr(self, criterion)
        people = np.array(people)
        score = np.array([sort_func(person) for person in people])
        sorted_people = people[np.argsort(score)]
        if flipped:
            sorted_people = np.flip(sorted_people)
        return sorted_people

    def get_location(self):
        return self.loc

    def get_coords(self):
        return self.get_location().get_coords()

    def lookup_key(self):
        raise NotImplementedError(self.__class__.__name__ + '.lookup_key')

    def distance_to_center_through(self, person):
        loc = self.get_location()
        other_loc = person.get_location()
        return loc.distance_to_center_through(other_loc)

    def distance_to_center_through_self(self, person):
        return person.distance_to_center_through(self)

    def distance_to(self, person):
        self_loc = self.get_location()
        other_loc = person.get_location()
        return self_loc.distance_to(other_loc)

    def get_preferences(self):
        return self.preferences

    def next_preference(self):
        return next(self.iterable_preferences)

    def serialize(self):
        raise NotImplementedError(self.__class__.__name__ + '.serialize')

    def __str__(self):
        return f"Person:<{self.get_location().x}, {self.get_location().y}>"

    def __repr__(self):
        return self.__str__()


class Driver(Person):

    def __init__(self, driver_id, loc, center_coords, name, district, num_gates, phone):
        Person.__init__(self, driver_id, loc, center_coords, name, district, phone)
        self.students = []
        self.student_dist_score_lookup = {}
        self.dist_score_lookup = {}
        self.student_time_score = {}
        self.base_time = None
        self.final_score_lookup = {}
        self.wait_time = None
        self.gate_score_list = [0] * num_gates
        self.friend_score_lookup = {}
        self.students_weekly = {}

    def reset_calculations(self):
        self.preferences = []
        self.iterable_preferences = None
        self.students = []
        self.student_dist_score_lookup = {}
        self.dist_score_lookup = {}
        self.student_time_score = {}
        self.base_time = None
        self.final_score_lookup = {}
        self.wait_time = None
        self.friend_score_lookup = {}

    def add_student(self, student):
        student.join_driver(self)
        self.students.append(student)

    def add_sorted_student(self, student):
        self.add_student(student)
        self.students = list(self.sorted_by_criterion(self.students, "final_score", flipped=True))

    def set_picked_students(self, students):
        self.students = students

    def remove_student(self, student):
        self.students.remove(student)
        student.leave_driver()

    def remove_least_score_student(self):
        least_score_student = self.students[-1]
        self.remove_student(least_score_student)
        return least_score_student

    def picked_students(self):
        return self.students

    def add_picked_students_weekly(self, day, students):
        self.students_weekly[day] = students

    def picked_students_weekly(self):
        return self.students_weekly

    def picked_students_weekly_on(self, day):
        return self.students_weekly[day]

    def is_better_student(self, student):
        # new_score = student.final_score(self)
        # existing_score = self.picked_students()[-1].final_score(self)
        # return new_score > existing_score
        new_rank = self.get_preferences().index(student)
        existing_rank = self.get_preferences().index(self.picked_students()[-1])
        return new_rank < existing_rank

    def is_full(self):
        return len(self.picked_students()) == 4

    def lookup_key(self):
        return str(self.get_coords())

    def calculate_student_dist_scores(self, students):
        distances = [self.distance_to_center_through(student) for student in students]
        len_dist = len(distances)
        total_dist = np.sum(distances)
        scores = []
        for i, student in enumerate(students):
            dist = distances[i]
            scores.append((total_dist - dist) / len_dist)
        # scores = softmax(scores)
        for i, student in enumerate(students):
            key = student.lookup_key()
            self.student_dist_score_lookup[key] = scores[i]

    def student_dist_score(self, student):
        key = student.lookup_key()
        return self.student_dist_score_lookup[key]

    def calculate_dist_scores(self, students):
        for student in students:
            driver_dist_score = student.driver_dist_score(self)
            student_dist_score = self.student_dist_score(student)
            final_dist_score = driver_dist_score * student_dist_score
            key = student.lookup_key()
            self.dist_score_lookup[key] = final_dist_score

    def dist_score(self, student):
        key = student.lookup_key()
        return self.dist_score_lookup[key]

    def calculate_time_scores(self, students):
        sum_weights = 0
        sum_weighted_time = 0
        for student in students:
            dist_score = self.dist_score(student)
            sum_weighted_time += (dist_score * student.get_numeric_time())
            sum_weights += dist_score
        base_time = sum_weighted_time / sum_weights
        for student in students:
            difference = abs(student.get_numeric_time() - base_time)
            student_time_score = np.exp(- difference)  # just to make less become higher
            key = student.lookup_key()
            self.student_time_score[key] = student_time_score
        self.base_time = base_time

    def time_score(self, student):
        key = student.lookup_key()
        return self.student_time_score[key]

    def get_base_time(self):
        return self.base_time

    def calculate_gate_scores(self, students):
        for student in students:
            dist_score = self.dist_score(student)
            self.gate_score_list[student.get_gate_group()] += dist_score
        self.gate_score_list = cubed_probability(self.gate_score_list)

    def gate_score(self, student):
        return self.gate_score_list[student.get_gate_group()]

    def calculate_friend_score(self, students):
        for student in students:
            student_dist_score = self.dist_score(student)
            scores = [student_dist_score]
            for friend in student.get_friends():
                friend_dist_score = self.dist_score(friend)
                if friend_dist_score >= student_dist_score:
                    scores.append(friend_dist_score)
            friend_score = np.mean(scores)
            key = student.lookup_key()
            self.friend_score_lookup[key] = friend_score

    def friend_score(self, student):
        key = student.lookup_key()
        return self.friend_score_lookup[key]

    def calculate_final_scores(self, students, consider_dist, consider_gate, consider_time, consider_friends):
        self.calculate_dist_scores(students)
        self.calculate_time_scores(students)
        self.calculate_gate_scores(students)
        self.calculate_friend_score(students)
        for student in students:
            dist_score = self.dist_score(student) if consider_dist else 1
            time_score = self.time_score(student) if consider_time else 1
            gate_score = self.gate_score(student) if consider_gate else 1
            friends_score = self.friend_score(student) if consider_friends else 1
            score = dist_score * time_score * gate_score * friends_score
            key = student.lookup_key()
            self.final_score_lookup[key] = score

    def final_score(self, student):
        key = student.lookup_key()
        return self.final_score_lookup[key]

    def set_preferences(self, students, consider_dist, consider_gate, consider_time, consider_friends):
        self.calculate_final_scores(students, consider_dist, consider_gate, consider_time, consider_friends)
        self.preferences = list(self.sorted_by_criterion(students, "final_score", flipped=True))
        self.iterable_preferences = iter(self.preferences.copy())

    def get_route(self, students=None):
        import itertools
        if students is None:
            students = self.picked_students()
        locations = [student.get_location() for student in students]
        paths = [list(perm) for perm in itertools.permutations(locations)]
        distances = []
        for path in paths:
            path.insert(0, self.get_location())
            center_x, center_y = self.center_coords[0], self.center_coords[1]
            path.append(Location(center_x, center_y, (center_x, center_y)))
            distance = 0
            for i in range(1, len(path)):
                distance += path[i].distance_to(path[i - 1])
            distances.append(distance)
        idx = np.argmin(distances)
        route = (paths[idx], distances[idx])
        return route

    def get_wait_time(self):
        if self.wait_time is None:
            # check if driver has no students
            if len(self.picked_students()) == 0:
                return 0
            times = [student.get_numeric_time() for student in self.picked_students()]
            max_time = max(times)
            diffs = [(max_time - t) for t in times]
            self.wait_time = sum(diffs)
        return self.wait_time

    def serialize(self):
        x, y = self.get_coords()
        path = []
        for loc in self.get_route()[0]:
            point_x, point_y = loc.get_coords()
            path.append({'lat': point_x, 'lng': point_y})
        students = [student.serialize() for student in self.picked_students()]
        serialized = {"name": self.get_name(),
                      "coords": {'lat': round(x, 5), 'lng': round(y, 5)},
                      "dist": round(self.get_route()[1], 2),
                      "phone": self.get_phone(),
                      "path": path,
                      "students": students,
                      "district": self.get_district(),
                      }
        return serialized

    def serialize_weekly(self):
        serialized = self.serialize()
        for key, val in self.picked_students_weekly().items():
            students = [student.serialize_weekly() for student in val]
            path = []
            for loc in self.get_route(val)[0]:
                point_x, point_y = loc.get_coords()
                path.append({'lat': point_x, 'lng': point_y})
            serialized[key] = {
                "path": path,
                "students": students
            }
        return serialized

    def __str__(self):
        return f"Driver: {self.get_name()}"


class Student(Person):
    def __init__(self, student_id, loc, center_coords, leave_time, name, district, gate_group,
                 phone, friend_names):
        Person.__init__(self, student_id, loc, center_coords, name, district, phone)
        self.leave_time = str(leave_time)
        self.driver_dist_score_lookup = {}
        self.gate_name = gate_group
        self.gate_group = int(gate_group)
        self.driver = None
        self.friend_names = friend_names
        self.friends = []
        self.driver_weekly = {}

    def reset_calculations(self, reset_driver_weekly=True):
        self.preferences = []
        self.iterable_preferences = None
        self.driver_dist_score_lookup = {}
        self.driver = None
        if reset_driver_weekly:
            self.driver_weekly = {}

    def get_friend_names(self):
        return self.friend_names

    def add_friend(self, friend):
        self.friends.append(friend)

    def get_friends(self):
        return self.friends

    def get_numeric_time(self):
        return string_to_numeric_time(self.get_time())

    def get_time(self):
        return self.leave_time

    def get_gate_name(self):
        return self.gate_name

    def get_gate_group(self):
        return self.gate_group

    def join_driver(self, driver):
        self.driver = driver

    def is_better_driver(self, new_driver):
        prev_driver = self.current_driver()
        preferences = self.get_preferences()
        prev_index = np.where(preferences == prev_driver)
        new_index = np.where(preferences == new_driver)
        return new_index < prev_index

    def current_driver(self):
        return self.driver

    def leave_driver(self):
        self.driver = None

    def add_driver_weekly(self, day, driver):
        self.driver_weekly[day] = driver

    def driver_weekly_on(self, day):
        return self.driver_weekly[day]

    def lookup_key(self):
        return str(self.get_coords()) + self.get_time()

    def calculate_driver_dist_scores(self, drivers):
        distances = [self.distance_to_center_through_self(driver) for driver in drivers]
        len_dist = len(distances)
        total_dist = np.sum(distances)
        scores = []
        for i, driver in enumerate(drivers):
            dist = distances[i]
            scores.append((total_dist - dist) / len_dist)
        # scores = softmax(scores)
        for i, driver in enumerate(drivers):
            key = driver.lookup_key()
            self.driver_dist_score_lookup[key] = scores[i]

    def driver_dist_score(self, driver):
        key = driver.lookup_key()
        return self.driver_dist_score_lookup[key]

    def final_score(self, driver):
        key = self.lookup_key()
        return driver.final_score_lookup[key]

    def set_preferences(self, drivers):
        self.preferences = list(self.sorted_by_criterion(drivers, "final_score", flipped=True))
        self.iterable_preferences = iter(self.preferences.copy())

    def serialize(self):
        x, y = self.get_coords()
        return {
            "name": self.get_name(),
            "coords": {'lat': round(x, 5), 'lng': round(y, 5)},
            "gate_name": self.get_gate_name(),
            "driver": self.current_driver().get_name() if self.current_driver() else "No Driver",
            "district": self.get_district(),
            "phone": self.get_phone(),
            "gate_group": self.get_gate_group(),
            "time": self.get_time(),
        }

    def serialize_weekly(self):
        serialized = self.serialize()
        for day in ["sa", "su", "mo", "tu", "we", "th"]:
            if day in self.driver_weekly:
                curr_driver = self.driver_weekly[day]
                # serialized[day] = self.driver_weekly[day].get_name()
                serialized[day] = {
                    "name": curr_driver.get_name(),
                    "phone": curr_driver.get_phone(),
                    "loc": curr_driver.get_district()
                }
            else:
                serialized[day] = ""
        return serialized

    def __str__(self):
        return f"Student: {self.get_name()}"

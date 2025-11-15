from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum, Case, When, IntegerField, Value
from qncy.models import Question, User, Tag, Answer, AnswerVote, QuestionVote

from random import choice, choices, randint
from faker import Faker


class Command(BaseCommand):
    help = "Fills the database with mock data"

    def add_arguments(self, parser):
        parser.add_argument("ratio", nargs=1, type=int)

    def handle(self, *args, **options):
        fake = Faker()
        ratio = options["ratio"][0]

        # counts
        n_users = ratio
        n_tags = ratio
        n_questions = ratio * 10
        n_answers = ratio * 100
        n_votes = ratio * 200

        self.stdout.write(self.style.NOTICE("Starting DB fill..."))

        with transaction.atomic():
            # 1) create users + tags
            user_objs = []
            tag_objs = []
            for _ in range(n_users):
                u = User(
                    email=fake.email(),
                    username=fake.user_name() + str(randint(1, 71)),
                    password="demopassword",
                )
                # While technically better, this is EXTREMELY slow,
                # and the reason this function has been taking so long to run.
                # Demo data shouldn't be secure anyway, right?
                # u.set_password("demopassword")
                user_objs.append(u)

                tag_name = (
                    " ".join(fake.words(randint(1, 3))) + " " + str(randint(1, 326))
                )
                tag_objs.append(Tag(name=tag_name))

            User.objects.bulk_create(user_objs, batch_size=500)
            Tag.objects.bulk_create(tag_objs, batch_size=1000)

            users = list(User.objects.order_by("-id")[:n_users])
            tags = list(Tag.objects.order_by("-id")[:n_tags])
            self.stdout.write(
                self.style.SUCCESS(f"Created {n_users} users and {n_tags} tags")
            )

            question_objs = []
            for _ in range(n_questions):
                question_objs.append(
                    Question(
                        author=choice(users),
                        title=fake.sentence(),
                        content=fake.text(),
                    )
                )
            Question.objects.bulk_create(question_objs, batch_size=1000)
            questions = list(Question.objects.order_by("-id")[:n_questions])
            self.stdout.write(self.style.SUCCESS(f"Created {n_questions} questions"))

            answer_objs = []
            for _ in range(n_answers):
                answer_objs.append(
                    Answer(
                        question=choice(questions),
                        author=choice(users),
                        content=fake.paragraph(),
                    )
                )
            Answer.objects.bulk_create(answer_objs, batch_size=1000)
            answers = list(Answer.objects.order_by("-id")[:n_answers])
            self.stdout.write(self.style.SUCCESS(f"Created {n_answers} answers"))

            answer_votes = []
            question_votes = []
            for _ in range(n_votes):
                if choice([True, False]):
                    av = AnswerVote(
                        answer=choice(answers),
                        user=choice(users),
                        up=(randint(1, 5) > 1),
                    )
                    answer_votes.append(av)
                else:
                    qv = QuestionVote(
                        question=choice(questions),
                        user=choice(users),
                        up=(randint(1, 5) > 1),
                    )
                    question_votes.append(qv)

            AnswerVote.objects.bulk_create(
                answer_votes, ignore_conflicts=True, batch_size=2000
            )
            QuestionVote.objects.bulk_create(
                question_votes, ignore_conflicts=True, batch_size=2000
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {len(answer_votes) + len(question_votes)} votes"
                )
            )

            through = Question.tags.through
            through_objs = []
            for q in questions:
                chosen = choices(tags, k=randint(1, 4))
                for t in chosen:
                    through_objs.append(through(question_id=q.id, tag_id=t.id))
            through.objects.bulk_create(
                through_objs, ignore_conflicts=True, batch_size=2000
            )

            answer_votes_agg = AnswerVote.objects.values("answer").annotate(
                rating=Sum(
                    Case(
                        When(up=True, then=Value(1)),
                        When(up=False, then=Value(-1)),
                        output_field=IntegerField(),
                    )
                )
            )
            answer_rating_map = {
                item["answer"]: item["rating"] or 0 for item in answer_votes_agg
            }

            for a in answers:
                a.rating = answer_rating_map.get(a.id, 0)
            Answer.objects.bulk_update(answers, ["rating"], batch_size=1000)

            qvotes_agg = QuestionVote.objects.values("question").annotate(
                rating=Sum(
                    Case(
                        When(up=True, then=Value(1)),
                        When(up=False, then=Value(-1)),
                        output_field=IntegerField(),
                    )
                )
            )
            qvote_map = {item["question"]: item["rating"] or 0 for item in qvotes_agg}

            answer_sum_by_question = Answer.objects.values("question").annotate(
                sum_rating=Sum("rating")
            )
            ans_sum_map = {
                item["question"]: item["sum_rating"] or 0
                for item in answer_sum_by_question
            }

            questions_to_update = []
            for q in questions:
                q.rating = qvote_map.get(q.id, 0) + ans_sum_map.get(q.id, 0)
                questions_to_update.append(q)
            Question.objects.bulk_update(
                questions_to_update, ["rating"], batch_size=1000
            )

            q_by_user = Question.objects.values("author").annotate(
                sum_rating=Sum("rating")
            )
            a_by_user = Answer.objects.values("author").annotate(
                sum_rating=Sum("rating")
            )

            user_rating_map = {}
            for item in q_by_user:
                user_rating_map[item["author"]] = user_rating_map.get(
                    item["author"], 0
                ) + (item["sum_rating"] or 0)
            for item in a_by_user:
                user_rating_map[item["author"]] = user_rating_map.get(
                    item["author"], 0
                ) + (item["sum_rating"] or 0)

            for u in users:
                u.rating = user_rating_map.get(u.id, 0)
            User.objects.bulk_update(users, ["rating"], batch_size=500)

            self.stdout.write(
                self.style.SUCCESS("Tagged and rated all questions, answers and users")
            )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully filled db with ratio of {ratio}")
        )

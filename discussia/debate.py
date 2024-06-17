from participant import Participant

class Debate:
    def __init__(self, openai_client, objective, model="gpt-3.5-turbo", max_iterations=10):
        self.openai_client = openai_client
        self.model = model
        self.language = self.detect_language(objective)
        self.objective = objective
        self.max_iterations = max_iterations
        self.messaages = []

    def detect_language(self, text):
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"Your must answer only with the language (Spanish, English, Italian, etc...) of the text: {text}"},
            ],
        )

        return response.choices[0].message.content

    def start(self):
        participants = ""

        index = 0
        for participant in self.participants:
            participants += f"Partcipant {index}: {participant.point_of_view}\n"
            index += 1
        system_prompt = f""""
        You're a judge in a debate between two or more AI models. The debate is about to start.
        Your objective is to generate questions to the participants to make them defend their point of view.
        # Participants:
        {participants}
        # Objective of debate.
        {self.objective}
        # Requirements.
        - You must ask questions to the participants. Only questions are allowed.
        - You must use the following language: {self.language}
        - You'll receive the answers of the participants, identify by participantX, where X is the number of the participant.
        - After ending a debate, you must add a conclusion to the debate.
        - Your role internally will be assistant.
        - You must include only one question per message.
        - You can answer empty if you think the debate is over.
        - Debate will conclude after {self.max_iterations} iterations or when the judge ends the debate.
        - You must be parcial and neutral.
        - If the user ask for next question, you only can ask with a JSON format, or an empty message to end the debate.
        - Your question must follow the following format:
          {{
            "question": "Your question",
            "participant": "participantX" // You can use "all" if you want to ask a question to all participants.
          }}
        """
        self.messaages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

    def get_next_question(self):
        self.messaages.append({
            "role": "user",
            "content": "Next question",
        })
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=self.messaages,
        )

        self.messaages.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        })

        json = response.choices[0].message.content
        if '```json\n' in json:
            json = json.replace('```json\n', '')
            json = json.replace('```', '')

        return json
    def end(self):
        self.messaages.append({
            "role": "user",
            "content": "Add a conclusion to the debate, please be subjective including the key points of the debate. And which participant you think won the debate. You can evaluate the partcipants giving a score from 1 to 10."
        })

        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=self.messaages,
        )

        self.messaages.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        })

        return response.choices[0].message.content
    def add_answer(self, participant, answer):
        self.messaages.append({
            "role": "user",
            "content": f"Paticipant {participant}: {answer}",
        })

    def to_csv(self):
        self.messaages.append({
            "role": "user",
            "content": "Generate a CSV comparing the answers of the participants, in an abstract way, just key points. Don't include anymore information. You must escape strings with double quotes."
        })

        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=self.messaages,
        )

        self.messaages.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        })

        csv = response.choices[0].message.content

        if '```csv' in csv:
            csv = csv.split('```csv')[1]
            csv = csv.split('```')[0]
            csv = csv.strip()

        return csv


    def set_participants(self, participants):
        self.participants = list(map(lambda participant: Participant(self, participant), participants))

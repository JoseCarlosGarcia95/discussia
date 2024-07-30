class Participant:
    def __init__(self, debate, point_of_view):
        self.debate = debate
        self.point_of_view = point_of_view
        self.messages = []

    def start(self):
        system_prompt = f"""
        You're a participant in a debate between two or more AI models. The debate is about to start.
        Your objective is to defend your point of view and attack the point of view of the other participants.
        
        # Objective of the debate
        {self.debate.objective}
        
        # Your point of view
        {self.point_of_view}
        
        # Requirements
        - You must defend your point of view and attack the point of view of the other participants.
        - You must use the following language: {self.debate.language}
        - If you think the debate is over, you can end it by typing "ENDDEBATE" at the beginning of your answer.
        - You'll receive questions from the judge, identified by "JUDGE".
        - You'll receive answers from the other participants, identified by "participantX", where X is the participant's number.
        - Your role internally will be assistant.
        """

        self.messages = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

    def add_answer(self, participant, answer):
        self.messages.append({
            "role": "user",
            "content": f"Paticipant {participant}: {answer}",
        })

    def answer(self, question):
        self.messages.append({
            "role": "user",
            "content": f"Judge: {question}"
        })

        response = self.debate.openai_client.chat.completions.create(
            model=self.debate.model,
            messages=self.messages,
        )

        self.messages.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        })

        return response.choices[0].message.content

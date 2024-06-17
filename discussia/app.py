import click
import os
import json
from openai import OpenAI
from debate import Debate

@click.group()
def cli():
    """CLI application to generate a debate for making decisions between two or more IA models."""
    pass

@cli.command(help="Generate a debate for making decisions between two or more IA models.")
@click.option(
    "-o",
    "--objective",
    help="The objective of the debate.",
    default=None,
)
@click.option(
    "-n",
    "--num-participants",
    help="The number of participants in the debate.",
    default=0,
)
@click.option(
    "-p",
    "--participants",
    help="The participants in the debate.",
    default=None,
)
@click.option(
    "-m",
    "--model",
    help="The model to use for the debate.",
    default="",
)
@click.option(
    "-i",
    "--max-iterations",
    help="The maximum number of iterations to generate a debate.",
    default=0,
)
def interactive(objective, num_participants, participants, model, max_iterations):
    api_key = os.getenv("OPENAI_API_KEY") or click.prompt(
        "Please enter the OpenAI API key"
    )

    openai_client = OpenAI(api_key=api_key)

    model = model or click.prompt("Please enter the model to use for the debate", default="gpt-4o")

    objective = objective or click.prompt("Please enter the objective of the debate")

    debate = Debate(openai_client, objective, model=model, max_iterations=max_iterations)

    num_participants = num_participants > 0 or int(click.prompt(
        "Please enter the number of participants in the debate",
        type=int,
        default=2,
    ))

    if participants is None:
        participants = []
        for i in range(num_participants):
            participants.append(click.prompt(f"Please enter participant {i + 1}"))

    max_iterations = max_iterations > 0 or int(click.prompt(
        "Please enter the maximum number of iterations to generate a debate",
        type=int,
        default=10,
    ))
    debate.set_participants(participants)

    click.echo("Discussion is ready to generate a debate for you.")
    click.echo(f"|_ Objective: {debate.objective}")

    index = 0

    for participant in debate.participants:
        click.echo(f"|__ Participant {index}: {participant.point_of_view}")
        index += 1

    debate.start()

    for participant in debate.participants:
        participant.start()

    iteration = 0.0
    while iteration < max_iterations:
        question = debate.get_next_question()

        if len(question) == 0:
            break
        question_obj = json.loads(question)

        who_must_answer = []

        if "participant" not in question_obj:
            break
        if question_obj["participant"] == "all":
            who_must_answer = range(len(debate.participants))
        else:
            who_must_answer = [int(question_obj["participant"].replace("participant", ""))]

        iteration += len(who_must_answer) / len(debate.participants)

        click.echo(f"|___ Question: {question_obj['question']}")
        for participant in who_must_answer:
            participant_obj = debate.participants[participant]
            answer = participant_obj.answer(question_obj["question"])

            click.echo(f"|____ Answer from participant {participant}: {answer}")
            debate.add_answer(participant, answer)

            index = 0
            for participant_to_add_answ in debate.participants:
                if index != participant:
                    participant_to_add_answ.add_answer(participant_obj, answer)
                index += 1

    conclusion = debate.end()

    click.echo(f"|_ Conclusion: {conclusion}")

    click.echo("Debate is over. Thank you for using the application.")
    csv = debate.to_csv()

    with open("debate.csv", "w") as f:
        f.write(csv)

cli.add_command(interactive)

if __name__ == "__main__":
    cli()

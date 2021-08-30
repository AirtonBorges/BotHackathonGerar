from time import sleep
from discord.ext import commands
from keep_alive import keep_alive

import discord
import unidecode
import os 
import csv
import string
import random

BOT_KEY = os.getenv('BOT_KEY')

QUESTION_CHANNEL = 881942999708336168
QUIZ_CHANNEL = 881942837640462376

client = commands.Bot(command_prefix=["!"])

class is_running:
  quiz = False
  quiz_id = 0

@client.event
async def on_ready():
    print(f"Bot Ativado")


def remove_punctuaction(word):
  return word.translate(str.maketrans('', '', string.punctuation))


def remove_accents(args):
  phrase = args
  parsed_phrase = []
  
  for word in phrase:
    parsed_word = unidecode.unidecode(word)
    pw_without_punctuation = remove_punctuaction(parsed_word)
    parsed_phrase.append(pw_without_punctuation);

  return parsed_phrase


# Colocar todas as possiveis perguntas numa lista
def get_links():
    with open("ListOfLinksCopy.csv", 'r', encoding='utf-8') as searches_file:
        possible_searches = csv.reader(searches_file)

        searches_dict = {}
        
        for row in possible_searches:
          searches_dict.update({row[0]: [row[1], int(row[2])]})

        return searches_dict

def get_template(question, mixed_alternatives, number):
  return f'''
      - Pergunta {number}: {question}
      ```A: {mixed_alternatives[0]}``````B: {mixed_alternatives[1]}``````C: {mixed_alternatives[2]}``````D: {mixed_alternatives[3]}```'''


def get_new_question(previous_questions):
   with open("ListOfQuestions.csv", 'r', encoding='utf-8') as questions_list:
        all_questions = csv.reader(questions_list)

        list_of_questions = list(all_questions)

        random_question = []
        while (True):      
          random_question = random.choice(list_of_questions)
  
          if random_question in previous_questions:
            print("- Got repeated question.\n")
          elif len(random_question) < 5:
            print(f"- Not Enough alternatives on question: {random_question}\n")
          else: 
            break
        
        question = random_question[0]
        mixed_alternatives = random.sample(random_question[1:5], 4)
        answer = random_question[4]

        resulting_question = {"question":question, "mixed_alternatives":mixed_alternatives, "answer":answer}

        print(resulting_question)
    
        return resulting_question


async def add_reactions(message, reactions):
  added_reactions = []
  
  for reaction in reactions:
    reaction_added = await message.add_reaction(reaction)
    added_reactions.append(reaction_added)
  
  return added_reactions

async def remove_reactions(reactions, user):
  for reaction in reactions:
    print(reaction)
    await reaction.remove(user)

@client.command(aliases=['Oi', 'olá', 'Olá', 'ola', 'Ola'])
async def oi(ctx, *args):
  name = ctx.message.author.name
  await ctx.send(f"Oi {name}!")


@client.command(aliases=['Pesquisar', 'Buscar', 'buscar', 'pesquisa', 'Pesquisa'])
async def pesquisar(ctx, *args):
  if (ctx.message.channel.id != QUESTION_CHANNEL):
    await ctx.send(f"Se quer me perguntar algo, voce pode ir para o canal <#{QUESTION_CHANNEL}>!")
    return;
  
  #print(args)
  question = remove_accents(args)

  print(question)

  links = get_links()
  probable_links = []

  for k in links.keys():
    #print(f"{k}\n")
    for w in question:
      if w in k:
        links[k][1] += 1

  for k, v in links.items():
    ##print(f"- {k}: {v[0]}, {v[1]}")
    if v[1] > 0:
      probable_links.append([v[1], v[0]])

    
  probable_links.sort()
  
  for k, v in links.items():
    print(f"\n- {k}: {v[0]}, {v[1]}")


  if (len(probable_links) <= 0):
    await ctx.send("Não achei nada sobre isso :(")
    return
  
  await ctx.send(f"Otima pergunta <@{ctx.author.id}>, encontrei esse link que pode ajudar! \n\n{probable_links[-1][1]}\n")


@client.group(invoke_without_command=True, aliases=["Quiz", "Perguntas"])
async def quiz(ctx, *args):
  if (ctx.message.channel.id != QUIZ_CHANNEL):
    await ctx.send(f"Tá afim de fazer um quiz e testar seu conhecimento sobre o meio ambiente? Inicie um !quiz no <#{QUIZ_CHANNEL}>!")
    return
  else:    
    await ctx.send(f"{14*'-'} QUIZ! {14*'-'}")
    await ctx.send(f"- Oi! Bem vindo ao quiz para testar seus conhecimentos! ```!quiz regras - Para saber mais sobre o jogo``````!quiz iniciar - Iniciar o jogo!``````!quiz cancelar - Parar o jogo a qualquer momento.```")



@quiz.command(aliases=["Cancelar"])
async def cancelar(ctx, *args):
  if is_running.quiz:
    await ctx.send("Ok, cancelando o quiz. Se estiver afim, só tentar de novo!")
    is_running.quiz = False
  else:
    await ctx.send("Voce precisa começar um quiz antes de parar! Caso esteja em duvida, digite !quiz regras")


@quiz.command(aliases=["Regras"])
async def regras(ctx, *args):
  await ctx.send("- As regras são simples: ```São 5 perguntas de multipla escolha``````Responda usando as 'reações'``````E ao responder todas, receba a sua pontuação final!```")


@quiz.command(aliases=["Iniciar", "Começar", "começar"])
async def iniciar(ctx, *args):
  if (is_running.quiz):
    # quiz_message = await ctx.fetch_message(is_running.id)


    await ctx.send("Já tem um quiz rolando! Se quiser iniciar um novo, só escrever: ```!quiz _cancelar``` e iniciar um novo !quiz")
    return
  
  is_running.quiz = True
  
  counter_msg = await ctx.send("'")
  for i in range(3, 0, -1):
      await counter_msg.edit(content=f"{'-'*17} {i} {'-'*17}")
      sleep(1)
  await counter_msg.edit(content=f"{'-'*10} COMEÇOU! {'-'*10}")
  

  questions = []

  question = await ctx.send("'")
  is_running.id = question

  points = 0
  for i in range(1, 6):
    question_info = get_new_question(questions)
    questions.append(question_info)

    question_text = get_template(question_info['question'], question_info['mixed_alternatives'], i)

    question_answer = question_info['answer']

    await question.edit(content=question_text)

    list_of_options = {"🇦":0, "🇧":1, "🇨":2, "🇩":3}
    

    if i == 1:
      await add_reactions(question, list_of_options.keys())

    while (True):
      reaction, user = await client.wait_for('reaction_add', timeout=100.0)
      
      if user.name == client.user.name:
        continue
      else:
        await reaction.remove(user)

      if ctx.author.name == user.name: 
        chosen_alternative = str(reaction.emoji) 
        if chosen_alternative in list_of_options.keys():
          chosen_answer = question_info["mixed_alternatives"][list_of_options[chosen_alternative]]

          print(chosen_answer)

          if chosen_answer == question_answer:
            points += 1

          break
        else:
          await ctx.send("Não adicione novos emojis, responda somente de A a D!")
      else:
        await ctx.send("Apenas quem iniciou o quiz pode responder!")

    if i == 5:
      while (True):
        cached_question = discord.utils.get(client.cached_messages, id=question.id)
        
        reactions = cached_question.reactions
        if len(reactions) == 0:
          break

        print(reactions)
        await remove_reactions(reactions, client.user)
        await remove_reactions(reactions, ctx.author)
  
  await counter_msg.edit(content=f"{'-'*10} ACABOU! {'-'*10}")
  await question.edit(content=f"- Resultado:```Você fez um total de {points} pontos```")

  is_running.quiz = False

keep_alive()
client.run(BOT_KEY)

import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

TOKEN = TOKEN.strip()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

echo_channels = set()

@bot.event
async def on_ready():
    print(f"{bot.user} 봇이 로그인했습니다!")

async def find_member(ctx, text):
    if ctx.message.mentions:
        return ctx.message.mentions[0]

    text = text.strip()

    if text.isdigit():
        member = ctx.guild.get_member(int(text))
        if member:
            return member

        try:
            return await ctx.guild.fetch_member(int(text))
        except:
            return None

    text = text.lower()

    return discord.utils.find(
        lambda m: text in m.display_name.lower() or text in m.name.lower(),
        ctx.guild.members
    )

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    if message.channel.id in echo_channels:
        await message.channel.send(message.content)

@bot.command()
async def echo_on(ctx):
    echo_channels.add(ctx.channel.id)
    await ctx.send("이 채널에서 모든 말 따라 하기를 시작합니다.")

@bot.command()
async def echo_off(ctx):
    if ctx.channel.id in echo_channels:
        echo_channels.remove(ctx.channel.id)
        await ctx.send("이 채널에서 모든 말 따라 하기를 종료합니다.")
    else:
        await ctx.send("현재 이 채널은 따라 하기 상태가 아닙니다.")


@bot.command(name="추방")
@commands.has_permissions(kick_members=True)
async def kick_user(ctx, *, text=None):
    if text is None:
        await ctx.send("사용법: !추방 닉네임/아이디/@멘션")
        return

    target = await find_member(ctx, text)


    if target is None:
        await ctx.send("사용자를 찾을 수 없습니다.")
        return


    if target == ctx.author:
        await ctx.send("자기 자신은 추방할 수 없습니다.")
        return


    if target == ctx.guild.owner:
        await ctx.send("서버 주인은 추방할 수 없습니다.")
        return


    if ctx.author != ctx.guild.owner and ctx.author.top_role <= target.top_role:
        await ctx.send("자신보다 역할이 같거나 높은 사용자는 추방할 수 없습니다.")
        return


    if ctx.guild.me.top_role <= target.top_role:
        await ctx.send("봇보다 역할이 같거나 높은 사용자는 추방할 수 없습니다.")
        return


    try:
        await target.kick(reason=f"{ctx.author}가 명령어로 추방함")
        await ctx.send(f"{target.display_name}님을 추방했습니다.")
    except:
        await ctx.send("추방할 수 없습니다. 봇 권한이나 역할 순서를 확인하세요.")

@kick_user.error
async def kick_user_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("이 명령어를 사용하려면 멤버 추방하기 권한이 필요합니다.")
    else:
        await ctx.send("명령어 오류입니다. 사용법: !추방 닉네임/아이디/@멘션")

bot.run(TOKEN)



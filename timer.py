import discord
import asyncio
from datetime import datetime, timedelta
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

timers = {}  # {user_id: [{"name": timer_name1, "task": timer_task1, "start_time": start_time1, "channel_id": channel_id1}, ...]}

@bot.command()
async def 타이머(ctx, channel_name: str, name: str):
    if ctx.author.id not in timers:
        timers[ctx.author.id] = []

    # 입력한 채널 이름으로 해당 채널을 찾음
    selected_channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
    
    if selected_channel:
        async def timer(timer_info):
            remaining_time = timer_info["seconds"] - (datetime.utcnow() - timer_info["start_time"]).total_seconds()
            if remaining_time > 60:  # 1분보다 큰 경우에만 1분 전 알림 보냄
                await asyncio.sleep(remaining_time - 60)  # 1분 전에 알림 메시지 전송
                role = ctx.guild.get_role(1142067176602349578)  # 역할 ID로 역할 가져오기
                if role:
                    await selected_channel.send(f"{role.mention}, 타이머 '{timer_info['name']}'이(가) 1분 후에 종료됩니다!")

            await asyncio.sleep(60)  # 메시지 후 1분 대기
            await selected_channel.send(f"{ctx.author.mention}, 타이머 '{timer_info['name']}' ({timer_info['hours']}시간 {timer_info['minutes']}분 {timer_info['seconds']}초)가 끝났습니다! 이 타이머는 '{selected_channel.name}' 채널에서 시작되었습니다.")

        start_time = datetime.utcnow()
        task_info = {"name": name, "seconds": 60 * 60, "start_time": start_time, "channel_id": selected_channel.id}  # 60분을 초로 변환
        task = bot.loop.create_task(timer(task_info))
        task_info["task"] = task
        timers[ctx.author.id].append(task_info)
        await selected_channel.send(f"{ctx.author.mention}, 타이머 '{name}' (60분)를 시작합니다. 타이머가 종료되기 1분 전에 역할 맨션 알림이 '{selected_channel.name}' 채널로 갈 예정입니다.")
    else:
        await ctx.send("유효하지 않은 채널 이름입니다.")

@bot.command()
async def 타이머종료(ctx, name: str):
    if ctx.author.id in timers:
        removed_tasks = []
        for task_info in timers[ctx.author.id]:
            if task_info["name"].lower() == name.lower():
                task_info["task"].cancel()
                removed_tasks.append(task_info)
        
        if removed_tasks:
            for removed_task in removed_tasks:
                timers[ctx.author.id].remove(removed_task)
                await ctx.send(f"{ctx.author.mention}, 타이머 '{removed_task['name']}'를 취소했습니다.")
        else:
            await ctx.send("해당 이름의 타이머를 찾을 수 없습니다.")
    else:
        await ctx.send("현재 실행 중인 타이머가 없습니다.")

@bot.command()
async def 타이머리스트(ctx):
    if ctx.author.id in timers and timers[ctx.author.id]:
        timer_list = []
        for index, task_info in enumerate(timers[ctx.author.id]):
            remaining_time = (task_info["seconds"] - (datetime.utcnow() - task_info["start_time"]).total_seconds())
            hours, remainder = divmod(remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            timer_list.append(f"{index}: '{task_info['name']}' ({int(hours)}시간 {int(minutes)}분 {int(seconds)}초 남음)")
        
        await ctx.send(f"{ctx.author.mention}, 현재 실행 중인 타이머 목록:\n" + "\n".join(timer_list))
    else:
        await ctx.send("현재 실행 중인 타이머가 없습니다.")

bot.run('봇 토큰')

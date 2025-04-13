import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CallbackContext,
    ChatJoinRequestHandler,
    ChatMemberHandler
)
from telegram.constants import ChatMemberStatus
from datetime import datetime

API_TOKEN = '8000554853:AAG7vmCauc8XcvpPA7VciU6Z0TYixtfqn80'
MAIN_CHANNEL_ID = -1002366098084  # Канал для рассылки
NOTIFICATION_CHANNEL_ID = -1002679234430  # Новый канал для уведомлений
PRIVATE_CHANNEL_ID = -1002594928531
ADMIN_ID = 7567695472
CHANNEL_LINK = 'https://t.me/+NUq2EXMs_to5MzYy'
WELCOME_IMAGE = 'welcome.png'
SUBSCRIBERS = set()
USER_DB = set()  # Все пользователи бота

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def error_handler(update: object, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if update and isinstance(update, Update):
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже."
            )
        except Exception as e:
            logger.error(f"Error sending error message: {e}")

async def notify_admin(action: str, user: dict, context: CallbackContext, feedback: str = None):
    try:
        text = (f"🚨 <b>СОБЫТИЕ:</b> {action}\n"
                f"▫️ <b>Пользователь:</b> {user['mention']}\n"
                f"▫️ <b>ID:</b> <code>{user['id']}</code>\n"
                f"▫️ <b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        
        if feedback:
            text += f"\n\n📝 <b>Отзыв:</b>\n{feedback}"
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=text,
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Admin notification error: {e}")

async def start(update: Update, context: CallbackContext) -> None:
    try:
        context.user_data.clear()
        user = update.effective_user
        USER_DB.add(user.id)
        
        keyboard = [[InlineKeyboardButton("🧠 Активировать доступ", callback_data='start_bot')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = await update.message.reply_photo(
            photo=open(WELCOME_IMAGE, 'rb'),
            caption=f"<b>🧠 Доброго времени суток, {user.first_name}.</b>\n\n"
                    "Вы находитесь в приватном пространстве экспертной психологии и рационального развития.\n\n"
                    "▫️ Доступные ресурсы:\n"
                    "1. <b>Экспертная рассылка</b> — психотехники и антиманипулятивные стратегии\n"
                    "2. <b>Закрытый канал</b> — практические инструменты с научными источниками",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        await save_message(update, context, message.message_id)
        logger.info(f"User {user.id} started the bot")
    except Exception as e:
        logger.error(f"Error in start: {e}")

async def save_message(update: Update, context: CallbackContext, message_id: int) -> None:
    try:
        if 'message_ids' not in context.user_data:
            context.user_data['message_ids'] = []
        context.user_data['message_ids'].append(message_id)
    except Exception as e:
        logger.error(f"Error saving message: {e}")

async def delete_previous_messages(update: Update, context: CallbackContext) -> None:
    try:
        for msg_id in context.user_data.get('message_ids', []):
            try:
                await context.bot.delete_message(update.effective_chat.id, msg_id)
            except Exception as e:
                logger.warning(f"Error deleting message: {e}")
        context.user_data['message_ids'] = []
    except Exception as e:
        logger.error(f"Error deleting messages: {e}")

async def main_menu(update: Update, context: CallbackContext) -> None:
    try:
        query = update.callback_query
        await query.answer()
        await delete_previous_messages(update, context)
        
        keyboard = [
            [InlineKeyboardButton("📩 Подписаться на рассылку", callback_data='subscribe')],
            [InlineKeyboardButton("🔑 Подать заявку в канал", url=CHANNEL_LINK)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=open(WELCOME_IMAGE, 'rb'),
            caption="<b>🔐 ПРИКЛАДНАЯ ПСИХОЛОГИЯ БЕЗ ЦЕНЗУРЫ</b>\n\n"
                    "1️⃣ <b>Экспертная рассылка:</b>\n"
                    "— Антиманипулятивные стратегии\n"
                    "— Нейрофизиологические лайфхаки\n"
                    "— Клинические кейсы\n\n"
                    "2️⃣ <b>Закрытый канал:</b>\n"
                    "— 1-2 инструмента из психологии ежедневно\n"
                    "— Ссылки на персоисточники (PubMed/Springer и др.)\n"
                    "— Биохимия поведения\n\n"
                    "⏺ Выберите действие:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        await save_message(update, context, message.message_id)
    except Exception as e:
        logger.error(f"Error in main_menu: {e}")

async def handle_chat_join_request(update: Update, context: CallbackContext) -> None:
    try:
        user = update.chat_join_request.from_user
        logger.info(f"Join request from user {user.id}")
        await context.bot.send_message(
            chat_id=user.id,
            text="<b>🛡 ПРОВЕРКА БЕЗОПАСНОСТИ</b>\n\n"
                 "Для доступа к закрытому каналу:\n"
                 "1. Подтвердите, что вы не робот\n"
                 "2. Пройдите автоматическую верификацию\n\n"
                 "▫️ <i>Система анализирует:\n"
                 "— Паттерны кликов\n"
                 "— Время реакции\n"
                 "— История аккаунта</i>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Я не робот", callback_data='verify_human')
            ]]),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Can't send message to {user.id}: {e}")

async def verify_human(update: Update, context: CallbackContext) -> None:
    try:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        logger.info(f"Verification started for user {user_id}")

        await context.bot.approve_chat_join_request(
            chat_id=PRIVATE_CHANNEL_ID,
            user_id=user_id
        )
        
        await notify_admin(
            action="ОДОБРЕНИЕ ЗАЯВКИ В КАНАЛ",
            user={'id': user_id, 'mention': query.from_user.mention_html()},
            context=context
        )
        
        await context.bot.send_message(
            chat_id=user_id,
            text="<b>🟢 ДОСТУП ОТКРЫТ</b>\n\n"
                 "<b>Теперь Вам доступны:</b>\n"
                 "— 1-2 инструмента из психологии ежедневно\n"
                 "— Ссылки на персоисточники (PubMed/Springer и др.)\n"
                 "— Биохимия поведения\n\n"
                 "<i>«Знание — инструмент. Применение — мастерство.»</i> 🧠⚙️",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📢 Перейти в канал", url=CHANNEL_LINK),
                InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu')
            ]]),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Verification error: {e}")
        await context.bot.send_message(
            chat_id=user_id,
            text="⚠️ Произошла ошибка при обработке запроса. Попробуйте позже."
        )

async def handle_subscription(update: Update, context: CallbackContext) -> None:
    try:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        SUBSCRIBERS.add(user_id)
        USER_DB.add(user_id)
        
        await notify_admin(
            action="ПОДПИСКА НА РАССЫЛКУ",
            user={'id': user_id, 'mention': query.from_user.mention_html()},
            context=context
        )
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="<b>✅ ПОДПИСКА АКТИВИРОВАНА</b>\n\n"
                 "▫️ В рассылку входит:\n"
                 "— Когнитивные техники 🧩\n"
                 "— Разбор клинических кейсов\n"
                 "— Экстренные рекомендации при необходимости\n\n"
                 "<i>Отписаться: /stop</i>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu'),
                InlineKeyboardButton("🔑 Подать заявку", url=CHANNEL_LINK)
            ]]),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Subscription error: {e}")

async def forward_from_main_channel(update: Update, context: CallbackContext) -> None:
    try:
        if update.channel_post and update.channel_post.chat.id == MAIN_CHANNEL_ID:
            for user_id in SUBSCRIBERS.copy():
                try:
                    await context.bot.copy_message(
                        chat_id=user_id,
                        from_chat_id=MAIN_CHANNEL_ID,
                        message_id=update.channel_post.message_id
                    )
                except Exception as e:
                    logger.error(f"Forward error to {user_id}: {e}")
                    SUBSCRIBERS.discard(user_id)
    except Exception as e:
        logger.error(f"Error in forward_from_main_channel: {e}")

async def handle_notification_channel_post(update: Update, context: CallbackContext) -> None:
    try:
        if update.channel_post and update.channel_post.chat.id == NOTIFICATION_CHANNEL_ID:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu')],
                [InlineKeyboardButton("🔑 Подать заявку", url=CHANNEL_LINK)]
            ])
            
            for user_id in USER_DB:
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="🚀 <b>НОВЫЙ ПСИХОЛОГИЧЕСКИЙ ИНСТРУМЕНТ!</b>\n\n"
                             "🧠 Только что в канале .mindset application:\n"
                             "▫️ Эксклюзивный психологический лайфхак\n"
                             "▫️ Научно доказанные техники\n"
                             "▫️ Уникальный кейс из практики\n\n"
                             "🔥 Не упусти возможность прокачать свои навыки!",
                        reply_markup=keyboard,
                        parse_mode='HTML'
                    )
                except Exception as e:
                    logger.error(f"Error sending to {user_id}: {e}")
    except Exception as e:
        logger.error(f"Error in handle_notification_channel_post: {e}")

async def stop(update: Update, context: CallbackContext) -> None:
    try:
        user_id = update.effective_user.id
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Да", callback_data='confirm_unsub')],
            [InlineKeyboardButton("❌ Нет", callback_data='cancel_unsub')]
        ])
        
        await context.bot.send_message(
            chat_id=user_id,
            text="<b>⚠️ ВЫ УВЕРЕНЫ?</b>\n\n"
                 "Вы действительно хотите отписаться от рассылки?",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Stop command error: {e}")

async def handle_unsub_confirmation(update: Update, context: CallbackContext) -> None:
    try:
        query = update.callback_query
        await query.answer()
        user = query.from_user
        user_id = user.id
        
        if query.data == 'confirm_unsub':
            SUBSCRIBERS.discard(user_id)
            await context.bot.send_message(
                chat_id=user_id,
                text="<b>🔴 ВЫ ОТПИСАНЫ</b>\n\n"
                     "Рассылка больше не будет приходить.\n"
                     "Чтобы возобновить подписку, используйте /start",
                reply_markup=InlineKeyboardMarkup(
                    [InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu')],
                    [InlineKeyboardButton("🔑 Подать заявку", url=CHANNEL_LINK)]
                ),
                parse_mode='HTML'
            )
            await notify_admin(
                action="ОТПИСКА ОТ РАССЫЛКИ",
                user={'id': user_id, 'mention': user.mention_html()},
                context=context
            )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text="<b>Подписка сохранена 🟢</b>",
                reply_markup=InlineKeyboardMarkup(
                    [InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu')],
                    [InlineKeyboardButton("🔑 Подать заявку", url=CHANNEL_LINK)]
                ),
                parse_mode='HTML'
            )
            
        await delete_previous_messages(update, context)
    except Exception as e:
        logger.error(f"Unsubscription error: {e}")

async def handle_chat_member_update(update: Update, context: CallbackContext) -> None:
    try:
        if update.chat_member.new_chat_member.status == ChatMemberStatus.LEFT:
            user = update.chat_member.from_user
            if update.chat_member.chat.id == PRIVATE_CHANNEL_ID:
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔑 Подать заявку снова", url=CHANNEL_LINK)
                ]])
                
                await context.bot.send_message(
                    chat_id=user.id,
                    text=f"<b>🌀 Ты уверен, что хочешь покинуть канал .mindset application?</b>\n\n"
                         "Это решение безвозвратно стирает твой прогресс. Еще не поздно вернуться.\n\n"
                         "▫️ Если тебя не устроил контент:\n"
                         "— Выскажи <a href='t.me/warpscythe'>администратору</a>\n"
                         "— Напиши свои пожелания ниже ⤵️\n\n"
                         "<i>У тебя одна попытка обратной связи</i> ⏳",
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
                await notify_admin(
                    action="ВЫХОД ИЗ КАНАЛА",
                    user={'id': user.id, 'mention': user.mention_html()},
                    context=context
                )
                
                context.user_data['feedback_allowed'] = True
    except Exception as e:
        logger.error(f"Chat member update error: {e}")

async def handle_feedback(update: Update, context: CallbackContext) -> None:
    try:
        user = update.effective_user
        if context.user_data.get('feedback_allowed', False):
            feedback_text = update.message.text
            await notify_admin(
                action="ОБРАТНАЯ СВЯЗЬ",
                user={'id': user.id, 'mention': user.mention_html()},
                context=context,
                feedback=feedback_text
            )
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu'),
                 InlineKeyboardButton("🔑 Подать заявку повторно", url=CHANNEL_LINK)]
            ])
            await context.bot.send_message(
                chat_id=user.id,
                text="<b>📬 Ваше сообщение доставлено</b>\nСпасибо за обратную связь!",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            context.user_data['feedback_allowed'] = False
        else:
            await update.message.delete()
    except Exception as e:
        logger.error(f"Feedback error: {e}")

def main():
    application = Application.builder().token(API_TOKEN).build()

    # Основные обработчики
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('stop', stop))
    application.add_handler(CallbackQueryHandler(main_menu, pattern='^start_bot$'))
    application.add_handler(CallbackQueryHandler(main_menu, pattern='^main_menu$'))
    application.add_handler(CallbackQueryHandler(handle_subscription, pattern='^subscribe$'))
    application.add_handler(CallbackQueryHandler(verify_human, pattern='^verify_human$'))
    application.add_handler(CallbackQueryHandler(handle_unsub_confirmation, pattern='^(confirm_unsub|cancel_unsub)$'))
    application.add_handler(ChatJoinRequestHandler(handle_chat_join_request))
    
    # Обработчики каналов
    application.add_handler(MessageHandler(
        filters.Chat(MAIN_CHANNEL_ID) & filters.ChatType.CHANNEL,
        forward_from_main_channel
    ))
    application.add_handler(MessageHandler(
        filters.Chat(NOTIFICATION_CHANNEL_ID) & filters.ChatType.CHANNEL,
        handle_notification_channel_post
    ))
    
    application.add_handler(ChatMemberHandler(handle_chat_member_update, ChatMemberHandler.CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback))
    
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
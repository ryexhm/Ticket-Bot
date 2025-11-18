token = 'your bot token goes here'
import telegram,json,gspread
from google.oauth2.service_account import Credentials

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext,CallbackQueryHandler,ConversationHandler,ChatMemberHandler

scopes = ['https://www.googleapis.com/auth/spreadsheets']
sheetID = 'ID of your google sheet'
client = gspread.authorize(Credentials.from_service_account_file("key.json",scopes=scopes))
sheet = client.open_by_key(sheetID)

seatRows = 10
seatColumns = 10
columnNames = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


values = sheet.sheet1.row_values(1)
print(values)

def handle_responses(text:str) -> str:
	if 'hello' in text:
		return 'hello'

MENU, N1, N2, O1, O2, O3, O4= range(7)

def zoneConv(zone:str):
	zone = zone.lower()
	if zone == 'pz':
		zone = 'PLATINUM'
	if zone == 'bz':
		zone = 'BLUE'
	if zone == 'gz':
		zone = "GOLD"
	if zone == "gr":
		zone = "GREEN"
	if zone == "rz":
		zone = "RED"
	return zone

async def start_command(u:telegram.Update,ctx:CallbackContext):
	keyboard = [
        [InlineKeyboardButton("April 24", callback_data="n1")],
        [InlineKeyboardButton("April 26", callback_data="n2")],
    ]
	await u.message.reply_text('Hello! Which night would you like to book?',reply_markup=InlineKeyboardMarkup(keyboard))
	return MENU

async def button(u: telegram.Update, ctx: CallbackContext) -> int:
	selected = 0
	query = u.callback_query
	idd = str(u.effective_user.id)
	await query.answer()

	if query.data == "n1":
		await query.edit_message_text(text="📆 You have selected APRIL 24.\n\n📞 Please enter your phone number below.")
		with open('data.json', 'r+') as f:
			print(u.effective_user.id)
			d = json.loads(f.read())
			with open('data.json', 'w') as f:
				print(u.effective_user.id)
				d[idd] = {'night':1}
				json.dump(d,f,indent=4)
		return N1
	elif query.data == 'n2':
		await query.edit_message_text(text="📆 You have selected APRIL 26.\n\n📞 Please enter your phone number below.")
		with open('data.json', 'r+') as f:
			print(u.effective_user.id)
			d = json.loads(f.read())
			with open('data.json', 'w') as f:
				print(u.effective_user.id)
				d[idd] = {'night':2}
				json.dump(d,f,indent=4)
		return N2
	elif query.data in ['pz','gz','bz','gr','rz']:
		with open('data.json', 'r+') as f:
			print(u.effective_user.id)
			d = json.loads(f.read())
			with open('data.json', 'w') as f:
				print(u.effective_user.id)
				d[idd]['zone'] = query.data
				json.dump(d,f,indent=4)
		await query.edit_message_text(text="How many seats would you like to book?")
		return O3
	else:
		pass
	selected = 1


def phonenumberHandler(text:str)->str:
	if len(text) == 7:
		if text[0] in ['7','9']:
			return 1


async def pnh(u: telegram.Update, ctx: CallbackContext) -> str:
	idd = str(u.effective_user.id)
	text: str= u.message.text
	if phonenumberHandler(text) == 1:
		with open('data.json', 'r+') as f:
			print(u.effective_user.id)
			d = json.loads(f.read())
			with open('data.json', 'w') as f:
				print(u.effective_user.id)
				d[idd]['phone'] = int(text)
				json.dump(d,f,indent=4)
		print(text)
		await u.message.reply_text("Please enter your full name below, this will be used to verify your booking")
	return O1

async def st(u: telegram.Update, ctx: CallbackContext) -> str:
	try:
		idd = str(u.effective_user.id)
		text = u.message.text
		with open('data.json', 'r+') as f:
				print(u.effective_user.id)
				d = json.loads(f.read())
				with open('data.json', 'w') as f:
					print(u.effective_user.id)
					d[idd]['seats'] = text
					json.dump(d,f,indent=4)
		await u.message.reply_text(f"Please standby while we verify your information\n\nName: {d[idd]['name']}\nPhone: {d[idd]['phone']}\nNight: {d[idd]['night']}\nZone: {zoneConv(d[idd]['zone'])}\nSeats: {d[idd]['seats']}")

		return O4
	except:
		pass

def nameHandler(text:str)->str:
	return text.lower()

async def nm(u: telegram.Update, ctx: CallbackContext) -> str:
	idd = str(u.effective_user.id)
	text = nameHandler(u.message.text)
	with open('data.json', 'r+') as f:
			print(u.effective_user.id)
			d = json.loads(f.read())
			with open('data.json', 'w') as f:
				print(u.effective_user.id)
				d[idd]['name'] = text
				json.dump(d,f,indent=4)
	print(text)
	keyboard = [
        [InlineKeyboardButton("PLATINUM - 125rf", callback_data="pz")],
        [InlineKeyboardButton("GOLD - 100rf", callback_data="gz")],[InlineKeyboardButton("BLUE - 50rf", callback_data="bz")],[InlineKeyboardButton("GREEN - 30rf", callback_data="gr")],[InlineKeyboardButton("RED - 20rf", callback_data="rz")],
    ]
	await u.message.reply_text('Which zone would you like to book?',reply_markup=InlineKeyboardMarkup(keyboard))
	return O2


async def cancel(u: telegram.Update, ctx: CallbackContext) -> int:
    await u.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

if __name__ == '__main__':
	print('booting...')
	b = Application.builder().token(token).build()
	conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command,block=False)],
        states={
            MENU: [CallbackQueryHandler(button)],
            N1: [MessageHandler(filters.TEXT, pnh)],
            N2: [MessageHandler(filters.TEXT, pnh)],
            O1: [MessageHandler(filters.TEXT,nm)],
            O2: [CallbackQueryHandler(button)],
            O3: [MessageHandler(filters.TEXT,st)],
            O4: [CommandHandler("start", start_command)],
        },
        fallbacks=[CommandHandler("start", start_command)],
        per_message=False,per_user=True
    )
	b.add_handler(conv_handler)
	b.run_polling(allowed_updates=telegram.Update.ALL_TYPES)
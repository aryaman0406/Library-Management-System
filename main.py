from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd
from pymongo import MongoClient

# Connecting to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Change connection string as needed
db = client['LibraryDB']
collection = db['Library']

# Ensure the required collection exists
collection.create_index('BK_ID', unique=True)

def issuer_card():
    Cid = sd.askstring('Issuer Card ID', 'What is the Issuer\'s Card ID?')
    if not Cid:
        mb.showerror('Issuer ID cannot be empty!', 'Please enter a valid Issuer Card ID.')
    else:
        return Cid

def display_records():
    global tree
    tree.delete(*tree.get_children())
    data = collection.find()
    for record in data:
        tree.insert('', END, values=(record['BK_NAME'], record['BK_ID'], record['AUTHOR_NAME'], record['BK_STATUS'], record['CARD_ID']))

def clear_fields():
    global bk_status, bk_id, bk_name, author_name, card_id
    bk_status.set('Available')
    bk_id.set('')
    bk_name.set('')
    author_name.set('')
    card_id.set('')
    bk_id_entry.config(state='normal')

def clear_and_display():
    clear_fields()
    display_records()

def view_record():
    global bk_name, bk_id, bk_status, author_name, card_id
    if not tree.focus():
        mb.showerror('Select a row!', 'Please select a record to view.')
        return
    current_item_selected = tree.focus()
    values_in_selected_item = tree.item(current_item_selected)
    selection = values_in_selected_item['values']
    bk_name.set(selection[0])
    bk_id.set(selection[1])
    author_name.set(selection[2])
    bk_status.set(selection[3])

def add_record():
    global bk_name, bk_id, author_name, bk_status, card_id
    if bk_status.get() == 'Issued':
        card_id.set(issuer_card())
    else:
        card_id.set('N/A')
    surety = mb.askyesno('Are you sure?', 'Confirm adding the record? Book ID cannot be changed later.')
    if surety:
        try:
            collection.insert_one({
                'BK_NAME': bk_name.get(),
                'BK_ID': bk_id.get(),
                'AUTHOR_NAME': author_name.get(),
                'BK_STATUS': bk_status.get(),
                'CARD_ID': card_id.get()
            })
            clear_and_display()
            mb.showinfo('Record Added', 'The new record has been added successfully.')
        except Exception as e:
            mb.showerror('Error!', f'Error adding record: {e}')

def update_record():
    def update():
        global bk_status, bk_name, bk_id, author_name, card_id
        if bk_status.get() == 'Issued':
            card_id.set(issuer_card())
        else:
            card_id.set('N/A')
        collection.update_one(
            {'BK_ID': bk_id.get()},
            {'$set': {
                'BK_NAME': bk_name.get(),
                'AUTHOR_NAME': author_name.get(),
                'BK_STATUS': bk_status.get(),
                'CARD_ID': card_id.get()
            }}
        )
        clear_and_display()
        edit.destroy()
        bk_id_entry.config(state='normal')

    view_record()
    bk_id_entry.config(state='disable')
    edit = Button(left_frame, text='Update Record', font=btn_font, bg=btn_hlb_bg, width=20, command=update)
    edit.place(x=50, y=375)

def remove_record():
    if not tree.selection():
        mb.showerror('Error!', 'Please select a record to delete.')
        return
    current_item = tree.focus()
    values = tree.item(current_item)
    selection = values['values']
    collection.delete_one({'BK_ID': selection[1]})
    tree.delete(current_item)
    mb.showinfo('Done', 'Record successfully deleted.')
    clear_and_display()

def delete_inventory():
    if mb.askyesno('Are you sure?', 'This action will delete all records and cannot be undone. Proceed?'):
        collection.delete_many({})
        clear_and_display()

def change_availability():
    if not tree.selection():
        mb.showerror('Error!', 'Please select a record to change availability.')
        return
    current_item = tree.focus()
    values = tree.item(current_item)
    bk_id = values['values'][1]
    bk_status = values['values'][3]
    if bk_status == 'Issued':
        if mb.askyesno('Confirm Return', 'Has the book been returned?'):
            collection.update_one({'BK_ID': bk_id}, {'$set': {'BK_STATUS': 'Available', 'CARD_ID': 'N/A'}})
    else:
        collection.update_one({'BK_ID': bk_id}, {'$set': {'BK_STATUS': 'Issued', 'CARD_ID': issuer_card()}})
    clear_and_display()

# Variables
lf_bg = 'LightSkyBlue'
rtf_bg = 'DeepSkyBlue'
rbf_bg = 'DodgerBlue'
btn_hlb_bg = 'SteelBlue'

lbl_font = ('Georgia', 13)
entry_font = ('Times New Roman', 12)
btn_font = ('Gill Sans MT', 13)

# Initializing the main GUI window
root = Tk()
root.title('Library Management System')
root.geometry('1010x530')
root.resizable(0, 0)

Label(root, text='LIBRARY MANAGEMENT SYSTEM', font=("Noto Sans CJK TC", 15, 'bold'), bg=btn_hlb_bg, fg='White').pack(side=TOP, fill=X)

# StringVars
bk_status = StringVar()
bk_name = StringVar()
bk_id = StringVar()
author_name = StringVar()
card_id = StringVar()

# Frames
left_frame = Frame(root, bg=lf_bg)
left_frame.place(x=0, y=30, relwidth=0.3, relheight=0.96)

RT_frame = Frame(root, bg=rtf_bg)
RT_frame.place(relx=0.3, y=30, relheight=0.2, relwidth=0.7)

RB_frame = Frame(root)
RB_frame.place(relx=0.3, rely=0.24, relheight=0.785, relwidth=0.7)

# Left Frame
Label(left_frame, text='Book Name', bg=lf_bg, font=lbl_font).place(x=98, y=25)
Entry(left_frame, width=25, font=entry_font, textvariable=bk_name).place(x=45, y=55)

Label(left_frame, text='Book ID', bg=lf_bg, font=lbl_font).place(x=110, y=105)
bk_id_entry = Entry(left_frame, width=25, font=entry_font, textvariable=bk_id)
bk_id_entry.place(x=45, y=135)

Label(left_frame, text='Author Name', bg=lf_bg, font=lbl_font).place(x=90, y=185)
Entry(left_frame, width=25, font=entry_font, textvariable=author_name).place(x=45, y=215)

Label(left_frame, text='Status of the Book', bg=lf_bg, font=lbl_font).place(x=75, y=265)
OptionMenu(left_frame, bk_status, 'Available', 'Issued').place(x=75, y=300)

Button(left_frame, text='Add new record', font=btn_font, bg=btn_hlb_bg, width=20, command=add_record).place(x=50, y=375)
Button(left_frame, text='Clear fields', font=btn_font, bg=btn_hlb_bg, width=20, command=clear_fields).place(x=50, y=435)

# Right Top Frame
Button(RT_frame, text='Delete book record', font=btn_font, bg=btn_hlb_bg, width=17, command=remove_record).place(x=8, y=30)
Button(RT_frame, text='Delete full inventory', font=btn_font, bg=btn_hlb_bg, width=17, command=delete_inventory).place(x=178, y=30)
Button(RT_frame, text='Update book details', font=btn_font, bg=btn_hlb_bg, width=17, command=update_record).place(x=348, y=30)
Button(RT_frame, text='Change Book Availability', font=btn_font, bg=btn_hlb_bg, width=19, command=change_availability).place(x=518, y=30)

# Right Bottom Frame
Label(RB_frame, text='BOOK INVENTORY', bg=rbf_bg, font=("Noto Sans CJK TC", 15, 'bold')).pack(side=TOP, fill=X)

tree = ttk.Treeview(RB_frame, selectmode=BROWSE, columns=('Book Name', 'Book ID', 'Author', 'Status', 'Issuer Card ID'))

XScrollbar = Scrollbar(tree, orient=HORIZONTAL, command=tree.xview)
YScrollbar = Scrollbar(tree, orient=VERTICAL, command=tree.yview)
XScrollbar.pack(side=BOTTOM, fill=X)
YScrollbar.pack(side=RIGHT, fill=Y)

tree.config(xscrollcommand=XScrollbar.set, yscrollcommand=YScrollbar.set)

tree.heading('Book Name', text='Book Name', anchor=CENTER)
tree.heading('Book ID', text='Book ID', anchor=CENTER)
tree.heading('Author', text='Author', anchor=CENTER)
tree.heading('Status', text='Status', anchor=CENTER)
tree.heading('Issuer Card ID', text='Issuer Card ID', anchor=CENTER)

tree.column('#0', width=0, stretch=NO)
tree.column('#1', width=225, stretch=NO)
tree.column('#2', width=70, stretch=NO)
tree.column('#3', width=150, stretch=NO)
tree.column('#4', width=105, stretch=NO)
tree.column('#5', width=132, stretch=NO)

tree.place(y=30, x=0, relheight=0.9, relwidth=1)

clear_and_display()

# Finalizing the window
root.mainloop()

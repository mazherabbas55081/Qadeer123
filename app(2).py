import streamlit as st
import pandas as pd
import sqlite3, hashlib, hmac, os, json
from datetime import datetime

st.set_page_config(page_title="SHOPORA | Online Store", page_icon="🛍️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700;800&display=swap');
.stApp{background:#f5f6fb;font-family:'DM Sans',sans-serif}
[data-testid="stSidebar"]{background:#19152f}
[data-testid="stSidebar"] *{color:white!important}
.hero{background:linear-gradient(115deg,#21134d,#6540d8,#9875ff);padding:34px;border-radius:22px;color:white;margin:8px 0 22px}
.hero h1{color:white!important;font-size:40px;font-weight:800;margin:0}
.hero p{color:#eee8ff}
.product{background:white;border:1px solid #ececf4;border-radius:16px;padding:12px;margin-bottom:12px}
.price{color:#5934c9;font-size:21px;font-weight:800}
.muted{color:#777;font-size:12px}
div.stButton>button{border-radius:10px;font-weight:700}
div.stButton>button[kind="primary"]{background:#6841dc;color:white;border:0}
</style>
""", unsafe_allow_html=True)

DB="shopora.db"
def connect(): return sqlite3.connect(DB, check_same_thread=False)
with connect() as c:
    c.execute("CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY,name TEXT,salt TEXT,pwhash TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT,email TEXT,created TEXT,total REAL,items TEXT,customer TEXT,address TEXT,phone TEXT)")

def pw_hash(p,s): return hashlib.pbkdf2_hmac("sha256",p.encode(),bytes.fromhex(s),160000).hex()
def signup(name,email,pw):
    salt=os.urandom(16).hex()
    try:
        with connect() as c: c.execute("INSERT INTO users VALUES(?,?,?,?)",(email.lower().strip(),name.strip(),salt,pw_hash(pw,salt)))
        return True
    except sqlite3.IntegrityError: return False
def signin(email,pw):
    with connect() as c: row=c.execute("SELECT name,salt,pwhash FROM users WHERE email=?",(email.lower().strip(),)).fetchone()
    return row[0] if row and hmac.compare_digest(pw_hash(pw,row[1]),row[2]) else None

# Product photos are real image URLs hosted by Unsplash; internet is needed to display them.
P=[
(1,"Wireless Headphones","Electronics",8990,11990,4.8,248,"SoundMax","https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=85","Wireless over-ear headphones with rich sound and comfortable cushions."),
(2,"Smart Watch","Electronics",12499,15999,4.6,186,"Pulse","https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=85","A modern smart watch for everyday notifications and activity tracking."),
(3,"Digital Camera","Electronics",84999,99999,4.7,92,"FocusPro","https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=800&q=85","Compact digital camera for photography and video."),
(4,"Bluetooth Speaker","Electronics",5499,6999,4.5,131,"Boom","https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=800&q=85","Portable speaker for home and outdoor listening."),
(5,"Running Sneakers","Fashion",6499,8999,4.4,315,"Stride","https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=800&q=85","Lightweight everyday running shoes."),
(6,"Leather Handbag","Fashion",7299,9999,4.6,87,"Mode","https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=800&q=85","A versatile handbag for daily use."),
(7,"Sunglasses","Fashion",2999,3999,4.3,64,"Vista","https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=800&q=85","Classic lightweight sunglasses."),
(8,"Desk Lamp","Home & Living",3499,4499,4.5,74,"Glow","https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=800&q=85","Modern lamp for your study or work desk."),
(9,"Lounge Chair","Home & Living",28999,34999,4.7,42,"Casa","https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?auto=format&fit=crop&w=800&q=85","Contemporary accent chair for your room."),
(10,"Perfume","Beauty",6999,8999,4.6,156,"Aroma","https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&w=800&q=85","Elegant fragrance for gifting and everyday wear."),
(11,"Book Bundle","Books",2499,3299,4.8,98,"ReadMore","https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=800&q=85","A bundle of inspiring books for curious minds."),
(12,"Travel Backpack","Travel",3199,4299,4.4,142,"CarryOn","https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=800&q=85","Practical backpack with useful compartments."),
(13,"Yoga Mat","Sports",2199,2999,4.5,111,"Flex","https://images.unsplash.com/photo-1592432678016-e910b452f9a2?auto=format&fit=crop&w=800&q=85","Comfortable mat for yoga and home workouts."),
(14,"Water Bottle","Sports",1499,1999,4.5,221,"Hydro","https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=800&q=85","Reusable bottle for everyday hydration."),
(15,"Toy Car","Baby & Kids",3499,4599,4.4,83,"PlayWorks","https://images.unsplash.com/photo-1594787318286-3d835c1d207f?auto=format&fit=crop&w=800&q=85","Fun toy car for playtime and gifting.")
]
P=[dict(id=x[0],name=x[1],cat=x[2],price=x[3],old=x[4],rating=x[5],reviews=x[6],brand=x[7],img=x[8].replace("photo-1505740420928-5e560c06d30e","photo-1505740420928-5e560c06d30e"),desc=x[9],stock=20) for x in P]
def prod(pid): return next((x for x in P if x["id"]==pid),None)
def rs(n): return f"Rs. {n:,.0f}"

for k,v in {"user":None,"cart":{},"wish":[],"page":"Home","detail":None}.items():
    if k not in st.session_state: st.session_state[k]=v
def go(p): st.session_state.page=p; st.session_state.detail=None
def add(pid): st.session_state.cart[pid]=min(prod(pid)["stock"],st.session_state.cart.get(pid,0)+1); st.toast("Added to cart!")
def total(): return sum(prod(i)["price"]*q for i,q in st.session_state.cart.items())

with st.sidebar:
    st.markdown("# 🛍️ SHOPORA")
    st.caption("Your everyday online marketplace")
    if st.session_state.user: st.success("Hello, "+st.session_state.user["name"])
    else: st.info("Welcome, guest!")
    page=st.radio("MENU",["Home","All Products","Wishlist","My Cart","My Orders","Account"])
    if page!=st.session_state.page: go(page); st.rerun()
    st.markdown("---")
    st.write(f"🛒 Cart: {sum(st.session_state.cart.values())}")
    st.write(f"💜 Wishlist: {len(st.session_state.wish)}")
    st.caption("Prepared by Mazhar Abbas")

st.markdown("### SHOPORA  ·  Discover more. Shop smarter.")
a,b=st.columns([3,1])
with a: st.caption("Electronics • Fashion • Home • Beauty • Books • Sports • More")
with b: st.markdown(f"**🛒 {sum(st.session_state.cart.values())} items**")

def product_cards(items):
    if not items: st.info("No products found."); return
    cols=st.columns(4)
    for i,p in enumerate(items):
        with cols[i%4]:
            st.markdown('<div class="product">',unsafe_allow_html=True)
            st.image(p["img"],use_container_width=True)
            st.markdown(f"**{p['name']}**")
            st.markdown(f"<span style='color:#d99a13'>★ {p['rating']}</span> <span class='muted'>({p['reviews']} reviews)</span>",unsafe_allow_html=True)
            st.markdown(f"<span class='price'>{rs(p['price'])}</span> <del class='muted'>{rs(p['old'])}</del>",unsafe_allow_html=True)
            st.caption(p["cat"])
            if st.button("View product",key=f"view{p['id']}",use_container_width=True): st.session_state.detail=p["id"]; st.rerun()
            c1,c2=st.columns(2)
            with c1:
                if st.button("Add 🛒",key=f"add{p['id']}",use_container_width=True): add(p["id"]); st.rerun()
            with c2:
                if st.button("♡" if p["id"] not in st.session_state.wish else "♥",key=f"wish{p['id']}",use_container_width=True):
                    if p["id"] in st.session_state.wish: st.session_state.wish.remove(p["id"])
                    else: st.session_state.wish.append(p["id"])
                    st.rerun()
            st.markdown("</div>",unsafe_allow_html=True)

def detail_view(p):
    if st.button("← Back"): st.session_state.detail=None; st.rerun()
    x,y=st.columns([1,1.2])
    with x: st.image(p["img"],use_container_width=True)
    with y:
        st.caption(p["cat"]+"  ·  "+p["brand"])
        st.title(p["name"])
        st.markdown(f"⭐ **{p['rating']} / 5** · {p['reviews']} ratings")
        st.markdown(f"<span class='price'>{rs(p['price'])}</span> &nbsp; <del>{rs(p['old'])}</del>",unsafe_allow_html=True)
        st.write(p["desc"])
        st.write("Availability: In stock")
        q=st.number_input("Quantity",1,20,1,key="detailqty")
        if st.button("🛒 Add to cart",type="primary"):
            for _ in range(q): add(p["id"])
            st.rerun()
        if st.button("♡ Add to wishlist"):
            if p["id"] not in st.session_state.wish: st.session_state.wish.append(p["id"])
            st.toast("Saved to wishlist")
    st.subheader("Customer reviews")
    for name,stars,review in [("Ayesha K.","★★★★★","Excellent quality and neat packaging."),("Usman R.","★★★★☆","Good value. Product matched the description."),("Hira M.","★★★★★","Very happy with this purchase.")]:
        with st.container(border=True):
            st.write(f"**{name}** · {stars}")
            st.write(review)
    st.caption("These are sample demo reviews, not verified customer feedback.")

# Account
if st.session_state.page=="Account":
    st.markdown("<div class='hero'><h1>Your Shopora account</h1><p>Sign in or create an account to manage demo orders.</p></div>",unsafe_allow_html=True)
    if st.session_state.user:
        st.success(f"Signed in as {st.session_state.user['name']} ({st.session_state.user['email']})")
        if st.button("Sign out"): st.session_state.user=None; st.rerun()
    else:
        mode=st.radio("Choose",["Sign in","Sign up"],horizontal=True)
        if mode=="Sign up":
            with st.form("signup"):
                name=st.text_input("Full name"); email=st.text_input("Email"); pw=st.text_input("Password",type="password"); confirm=st.text_input("Confirm password",type="password")
                send=st.form_submit_button("Create account",type="primary")
            if send:
                if not name or "@" not in email: st.error("Enter your name and a valid email.")
                elif len(pw)<8: st.error("Password must be at least 8 characters.")
                elif pw!=confirm: st.error("Passwords do not match.")
                elif signup(name,email,pw): st.success("Account created. Now sign in.")
                else: st.error("This email is already registered.")
        else:
            with st.form("signin"):
                email=st.text_input("Email"); pw=st.text_input("Password",type="password")
                send=st.form_submit_button("Sign in",type="primary")
            if send:
                name=signin(email,pw)
                if name: st.session_state.user={"name":name,"email":email.lower().strip()}; st.success("Welcome back!"); st.rerun()
                else: st.error("Incorrect email or password.")
    st.info("Demo authentication uses a local SQLite database. Use hosted authentication and persistent storage before launching a real public store.")

elif st.session_state.page=="Home":
    st.markdown("<div class='hero'><h1>Find your next favourite thing.</h1><p>Big choices, great finds — shop all your essentials in one place.</p></div>",unsafe_allow_html=True)
    search=st.text_input("🔎 Search products and brands",placeholder="Search headphones, shoes, watch...")
    cat=st.selectbox("Shop by category",["All"]+sorted({p["cat"] for p in P}))
    items=[p for p in P if (cat=="All" or p["cat"]==cat) and (not search or search.lower() in (p["name"]+p["cat"]+p["brand"]).lower())]
    st.subheader("✨ Featured products")
    product_cards(items[:8])
    st.subheader("Shop departments")
    cs=st.columns(4)
    for i,c in enumerate(sorted({p["cat"] for p in P})):
        with cs[i%4]:
            if st.button("Explore "+c,key="cat"+c): st.session_state.filtercat=c; go("All Products"); st.rerun()

elif st.session_state.page=="All Products":
    st.markdown("<div class='hero'><h1>All products</h1><p>Discover products across popular departments.</p></div>",unsafe_allow_html=True)
    f1,f2,f3=st.columns([2,1,1])
    with f1: search=st.text_input("Search")
    with f2: cat=st.selectbox("Category",["All"]+sorted({p["cat"] for p in P}))
    with f3: sort=st.selectbox("Sort",["Featured","Price low-high","Price high-low","Top rated"])
    lo,hi=st.slider("Price range (PKR)",0,100000,(0,100000),step=500)
    items=[p for p in P if (cat=="All" or p["cat"]==cat) and lo<=p["price"]<=hi and (not search or search.lower() in (p["name"]+p["brand"]+p["cat"]).lower())]
    if sort=="Price low-high": items.sort(key=lambda p:p["price"])
    if sort=="Price high-low": items.sort(key=lambda p:p["price"],reverse=True)
    if sort=="Top rated": items.sort(key=lambda p:p["rating"],reverse=True)
    st.caption(f"{len(items)} products found")
    product_cards(items)

elif st.session_state.page=="Wishlist":
    st.markdown("<div class='hero'><h1>Your wishlist</h1><p>Saved products for later.</p></div>",unsafe_allow_html=True)
    product_cards([prod(i) for i in st.session_state.wish if prod(i)])

elif st.session_state.page=="My Cart":
    st.markdown("<div class='hero'><h1>Your shopping cart</h1><p>Review items before checkout.</p></div>",unsafe_allow_html=True)
    if not st.session_state.cart: st.info("Your cart is empty.")
    else:
        for pid in list(st.session_state.cart):
            p=prod(pid)
            with st.container(border=True):
                x,y,z=st.columns([1,3,1])
                with x: st.image(p["img"],use_container_width=True)
                with y: st.write("**"+p["name"]+"**"); st.write(rs(p["price"]))
                with z:
                    q=st.number_input("Qty",0,p["stock"],st.session_state.cart[pid],key=f"qty{pid}")
                    st.session_state.cart[pid]=q
                    if st.button("Remove",key=f"rm{pid}"): st.session_state.cart.pop(pid); st.rerun()
        st.session_state.cart={i:q for i,q in st.session_state.cart.items() if q>0}
        sub=total(); delivery=0 if sub>=10000 else (250 if sub else 0)
        st.markdown(f"### Subtotal: {rs(sub)}  \nDelivery: {rs(delivery)}  \n## Total: {rs(sub+delivery)}")
        if st.button("Proceed to checkout",type="primary",disabled=not st.session_state.cart):
            if not st.session_state.user: st.warning("Please sign in first."); go("Account"); st.rerun()
            else: go("Checkout"); st.rerun()

elif st.session_state.page=="Checkout":
    st.markdown("<div class='hero'><h1>Checkout</h1><p>Enter delivery information to place a demo order.</p></div>",unsafe_allow_html=True)
    if not st.session_state.user: st.warning("Sign in first.")
    elif not st.session_state.cart: st.info("Your cart is empty.")
    else:
        with st.form("checkout"):
            customer=st.text_input("Full name",st.session_state.user["name"])
            phone=st.text_input("Phone number")
            address=st.text_area("Delivery address")
            city=st.selectbox("City",["Karachi","Lahore","Islamabad","Rawalpindi","Other"])
            payment=st.radio("Payment (demo)",["Cash on Delivery","Bank transfer (demo)"])
            submit=st.form_submit_button("Place demo order",type="primary")
        if submit:
            if not customer or not phone or not address: st.error("Complete all delivery details.")
            else:
                sub=total(); amount=sub+(0 if sub>=10000 else 250)
                items=[{"product":prod(i)["name"],"quantity":q,"unit_price":prod(i)["price"]} for i,q in st.session_state.cart.items()]
                with connect() as c: c.execute("INSERT INTO orders(email,created,total,items,customer,address,phone) VALUES(?,?,?,?,?,?,?)",(st.session_state.user["email"],datetime.now().isoformat(timespec="seconds"),amount,json.dumps(items),customer,f"{address}, {city} / {payment}",phone))
                st.session_state.cart={}; st.success(f"Demo order placed! Total: {rs(amount)}"); st.balloons()

elif st.session_state.page=="My Orders":
    st.markdown("<div class='hero'><h1>My orders</h1><p>Your order history.</p></div>",unsafe_allow_html=True)
    if not st.session_state.user: st.info("Sign in to see your orders.")
    else:
        with connect() as c: rows=c.execute("SELECT id,created,total,items,address FROM orders WHERE email=? ORDER BY id DESC",(st.session_state.user["email"],)).fetchall()
        if not rows: st.info("No orders yet.")
        for oid,created,amount,items,address in rows:
            with st.expander(f"Order #{oid} · {rs(amount)} · {created}"):
                st.write(address); st.dataframe(pd.DataFrame(json.loads(items)),use_container_width=True,hide_index=True)

# Detail view overlay for any page
if st.session_state.detail is not None:
    p=prod(st.session_state.detail)
    if p: detail_view(p)

st.markdown("---")
st.markdown("<div style='text-align:center;color:#777;padding:18px'><b style='color:#5934c9'>🛍️ SHOPORA</b><br>Prepared by Mazhar Abbas<br><small>Demo store • Sample listings, sample reviews and simulated checkout</small></div>",unsafe_allow_html=True)
st.caption("This demo is not connected to Daraz/AliExpress/AliBaba sellers, live stock, courier services or a payment gateway. Product photos load from Unsplash and require internet.")

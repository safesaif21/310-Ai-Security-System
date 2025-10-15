# 🚀 Quick Start - AI Security System Dashboard

Get your beautiful Streamlit dashboard running in 2 steps!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Run the Dashboard

```bash
streamlit run dashboard.py
```

That's it! 🎉

The dashboard will automatically open in your browser at **http://localhost:8501**

## Using the Dashboard

1. **Click "Start Camera"** - Begins real-time monitoring
2. **Watch the magic happen:**
   - 📹 Live camera feed with detection overlays
   - ⚠️ Threat level meter (0-10)
   - 🔪 Weapon detection alerts
   - 📊 Real-time statistics
3. **Click "Stop Camera"** - Stops monitoring

## Troubleshooting

### Camera Permission Error
- Grant camera access to your terminal/Python
- Close other apps using the camera

### Slow Loading
- First run downloads YOLO model (~6MB)
- Subsequent runs are instant

### Port Already in Use
```bash
streamlit run dashboard.py --server.port 8502
```

## Features at a Glance

✅ **Live Camera Feed** - Real-time video with AI detection  
✅ **Threat Level** - Color-coded 0-10 scale  
✅ **Weapon Detection** - Knives, bats, scissors  
✅ **People Counter** - Tracks number of people  
✅ **Beautiful UI** - Modern dark theme with gradients  
✅ **Real-time Stats** - FPS, alerts, timestamps  

## Requirements

- Python 3.7+
- Webcam
- Modern browser

---

**Need more help?** See the full [README.md](README.md)

**Ready to go?** Just run: `streamlit run dashboard.py` 🚀


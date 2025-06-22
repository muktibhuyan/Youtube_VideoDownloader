def format_scene_breakdown(scenes):
    rows = """
    <table style='width:100%; border-collapse: collapse; background-color:#1a1a1a; color: #FFFFFF; border: 2px solid #FF8C00; font-size: 16px;box-shadow: 0 4px 8px rgba(0,0,0,0.3);'>
        <tr style='background-color:#FF8C00; color: #000000;'>
            <th style='padding: 8px; border: 1px solid  #FF8C00; color: #000000; font-weight: bold;'>⏱️ Timestamp</th>
            <th style='padding: 8px; border: 1px solid # #FF8C00; color: #000000; font-weight: bold;'>📝 Description</th>
        </tr>
    """
    pattern = re.compile(r"\*\*\[(.*?)\]\*\*:\s*(.*)")

    
    for scene in scenes:
        match = pattern.match(scene)
        if match:
            timestamp = match.group(1).strip()
            description = match.group(2).strip()
            rows += f"""
             <tr style='background-color:#1a1a1a;'>
                <td style='padding: 8px; border: 1px solid #444; color: #87CEEB; font-weight: bold;font-size: 16px;vertical-align: top;'>{timestamp}</td>
                <td style='padding: 8px; border: 1px solid #444; color: #87CEEB; font-weight: bold;font-size: 16px;line-height: 1.4;'>{description}</td>
            </tr>
             """
                
    rows += "</table>"
    return rows


import gradio as gr
import yt_dlp
import os
import tempfile
import shutil
from pathlib import Path
import re
import uuid
import json
from datetime import datetime
import google.generativeai as genai
from xhtml2pdf import pisa
from io import BytesIO


def generate_pdf_from_html(html_content):
    """Generate PDF with simplified HTML that works better with xhtml2pdf"""
    try:
        # Create a simplified version of the HTML for PDF generation
        # Remove complex CSS that xhtml2pdf can't handle
        simplified_html = html_content.replace(
            "background: linear-gradient(135deg, #2d3748, #1a202c);", 
            "background-color: #f5f5f5;"
        ).replace(
            "background: linear-gradient(90deg, #FF8C00, #87CEEB);", 
            "background-color: #FF8C00;"
        ).replace(
            "rgba(135, 206, 235, 0.1)", 
            "#f9f9f9"
        ).replace(
            "rgba(0, 0, 0, 0.3)", 
            "#ffffff"
        ).replace(
            "text-shadow: 2px 2px 4px rgba(0,0,0,0.5);", 
            ""
        ).replace(
            "box-shadow: 0 8px 32px rgba(255, 140, 0, 0.3);", 
            ""
        ).replace(
            "box-shadow: 0 4px 8px rgba(0,0,0,0.3);", 
            ""
        ).replace(
            "display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;", 
            "display: block;"
        ).replace(
            "background-color:#1a1a1a;", 
            "background-color:#ffffff;"
        ).replace(
            "color: #FFFFFF;", 
            "color: #000000;"
        ).replace(
            "background-color:#FF8C00; color: #000000;", 
            "background-color:#FF8C00; color: #000000;"
        ).replace(
            "color: #87CEEB;", 
            "color: #000080;"
        ).replace(
            "border: 2px solid #FF8C00;", 
            "border: 1px solid #FF8C00;"
        )
        
        # Remove table styling that causes issues
        simplified_html = re.sub(r"style='[^']*background-color:#1a1a1a[^']*'", "style='background-color:#ffffff;'", simplified_html)
        simplified_html = re.sub(r"style='[^']*color: #87CEEB[^']*'", "style='color: #000080; padding: 8px;'", simplified_html)
        
        # Wrap in a complete HTML document with PDF-friendly CSS
        pdf_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    size: A4;
                    margin: 1cm;
                }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    font-size: 12px;
                    line-height: 1.4;
                    color: #000000;
                    background-color: #ffffff;
                }}
                .report-container {{
                    background-color: #ffffff;
                    padding: 15px;
                    border: 2px solid #FF8C00;
                    border-radius: 8px;
                }}
                .header {{
                    text-align: center;
                    color: #FF8C00;
                    font-size: 20px;
                    font-weight: bold;
                    margin-bottom: 15px;
                    border-bottom: 2px solid #FF8C00;
                    padding-bottom: 8px;
                }}
                .info-card {{
                    background-color: #f9f9f9;
                    padding: 12px;
                    margin: 8px 0;
                    border-left: 3px solid #87CEEB;
                    border-radius: 4px;
                    page-break-inside: avoid;
                }}
                .info-title {{
                    color: #000080;
                    font-size: 14px;
                    font-weight: bold;
                    margin-bottom: 8px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 8px 0;
                    page-break-inside: avoid;
                }}
                th, td {{
                    padding: 6px 8px;
                    border: 1px solid #cccccc;
                    text-align: left;
                    vertical-align: top;
                    font-size: 11px;
                }}
                th {{
                    background-color: #FF8C00;
                    color: #000000;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .scene-table {{
                    margin-top: 15px;
                }}
                .scene-header {{
                    color: #000080;
                    font-size: 16px;
                    font-weight: bold;
                    text-align: center;
                    margin-bottom: 10px;
                }}
                div[style*="display: grid"] {{
                    display: block !important;
                }}
                div[style*="grid-template-columns"] > div {{
                    display: block !important;
                    margin-bottom: 10px !important;
                    width: 100% !important;
                }}
            </style>
        </head>
        <body>
            <div class="report-container">
                {simplified_html}
            </div>
        </body>
        </html>
        """
        
        result = BytesIO()
        pisa_status = pisa.CreatePDF(pdf_html, dest=result)
        print("PDF buffer length:", len(result.getvalue()))
        
        if pisa_status.err:
            print(f"PDF generation error: {pisa_status.err}")
            return None
            
        result.seek(0)
        return result
        
    except Exception as e:
        print(f"PDF generation exception: {e}")
        return None

class YouTubeDownloader:
    def __init__(self):
        self.download_dir = tempfile.mkdtemp()
        # Use temp directory for Gradio compatibility
        self.temp_downloads = tempfile.mkdtemp(prefix="youtube_downloads_")
        # Also create user downloads folder for copying
        self.downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads", "YouTube_Downloads")
        os.makedirs(self.downloads_folder, exist_ok=True)
        self.gemini_model = None
    
    def configure_gemini(self, api_key):
        """Configure Gemini API with the provided key"""
        try:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
            return True, "✅ Gemini API configured successfully!"
        except Exception as e:
            return False, f"❌ Failed to configure Gemini API: {str(e)}"
    
    def cleanup(self):
        """Clean up temporary directories and files"""
        try:
            if hasattr(self, 'download_dir') and os.path.exists(self.download_dir):
                shutil.rmtree(self.download_dir)
                print(f"✅ Cleaned up temporary directory: {self.download_dir}")
            if hasattr(self, 'temp_downloads') and os.path.exists(self.temp_downloads):
                shutil.rmtree(self.temp_downloads)
                print(f"✅ Cleaned up temp downloads directory: {self.temp_downloads}")
        except Exception as e:
            print(f"⚠️ Warning: Could not clean up temporary directory: {e}")

    def is_valid_youtube_url(self, url):
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return youtube_regex.match(url) is not None

    def generate_scene_breakdown_gemini(self, video_info):
        """Generate AI-powered scene breakdown using Gemini"""
        if not self.gemini_model:
            return self.generate_scene_breakdown_fallback(video_info)
        
        try:
            duration = video_info.get('duration', 0)
            title = video_info.get('title', '')
            description = video_info.get('description', '')[:1500]  # Increased limit for better context
            
            if not duration:
                return ["**[Duration Unknown]**: Unable to generate timestamped breakdown - video duration not available"]
            
            # Create enhanced prompt for Gemini
            prompt = f"""
            Analyze this YouTube video and create a highly detailed, scene-by-scene breakdown with precise timestamps and specific descriptions:
            
            Title: {title}
            Duration: {duration} seconds
            Description: {description}
            
            IMPORTANT INSTRUCTIONS:
            1. Create detailed scene descriptions that include:
               - Physical appearance of people (age, gender, clothing, hair, etc.)
               - Exact actions being performed
               - Dialogue or speech (include actual lines if audible, or infer probable spoken lines based on actions and setting; format them as "Character: line...")
               - Setting and environment details
               - Props, objects, or products being shown
               - Visual effects, text overlays, or graphics
               - Mood, tone, and atmosphere
               - Camera movements or angles (if apparent)
            2. Dialogue Emphasis:
               - Include short dialogue lines in **every scene** wherever plausible.
               - Write lines like: Character: "Actual or inferred line..."
               - If dialogue is not available, intelligently infer probable phrases (e.g., "Welcome!", "Try this now!", "It feels amazing!").
               - Do NOT skip dialogue unless it's clearly impossible.
            
            3. Timestamp Guidelines:
               - For videos under 1 minute: 2-3 second segments
               - For videos 1-5 minutes: 3-5 second segments  
               - For videos 5-15 minutes: 5-10 second segments
               - For videos over 15 minutes: 10-15 second segments
               - Maximum 20 scenes total for longer videos
            
            4. Format each scene EXACTLY like this:
               **[MM:SS-MM:SS]**: Detailed description including who is visible, what they're wearing, what they're doing, what they're saying (if applicable), setting details, objects shown, and any visual elements.
            
                      
            5. Write descriptions as if you're watching the video in real-time, noting everything visible and audible.
                        
            Based on the title and description, intelligently infer what would likely happen in each time segment. Consider the video type and create contextually appropriate, detailed descriptions.
            """
            
            response = self.gemini_model.generate_content(prompt)
            
            # Parse the response into individual scenes
            if response and response.text:
                scenes = []
                lines = response.text.split('\n')
                current_scene = ""
                
                for line in lines:
                    line = line.strip()
                    if line.strip().startswith("**[") and "]**:" in line:
                        # This is a new scene timestamp line
                        if current_scene:
                            scenes.append(current_scene.strip())
                        current_scene = line.strip()
                    elif current_scene:
                        # This is continuation of the current scene description
                        current_scene += "\n" + line.strip()

                # Add the last scene if exists
                if current_scene:
                    scenes.append(current_scene.strip())
                    
                return scenes if scenes else self.generate_scene_breakdown_fallback(video_info)
            else:
                return self.generate_scene_breakdown_fallback(video_info)
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self.generate_scene_breakdown_fallback(video_info)

    def generate_scene_breakdown_fallback(self, video_info):
        """Enhanced fallback scene generation when Gemini is not available"""
        duration = video_info.get('duration', 0)
        title = video_info.get('title', '').lower()
        description = video_info.get('description', '').lower()
        uploader = video_info.get('uploader', 'Content creator')
        
        if not duration:
            return ["**[Duration Unknown]**: Unable to generate timestamped breakdown"]
        
        # Determine segment length based on duration
        if duration <= 60:
            segment_length = 3
        elif duration <= 300:
            segment_length = 5
        elif duration <= 900:
            segment_length = 10
        else:
            segment_length = 15
            
        scenes = []
        num_segments = min(duration // segment_length + 1, 20)
        
        # Detect video type for better descriptions
        video_type = self.detect_video_type_detailed(title, description)
        
        for i in range(num_segments):
            start_time = i * segment_length
            end_time = min(start_time + segment_length - 1, duration)
            
            start_formatted = f"{start_time//60}:{start_time%60:02d}"
            end_formatted = f"{end_time//60}:{end_time%60:02d}"
            
            # Generate contextual descriptions based on video type and timing
            desc = self.generate_contextual_description(i, num_segments, video_type, uploader, title)
            
            scenes.append(f"**[{start_formatted}-{end_formatted}]**: {desc}")
        
        return scenes

    def detect_video_type_detailed(self, title, description):
        """Detect video type with more detail for better fallback descriptions"""
        text = (title + " " + description).lower()
        
        if any(word in text for word in ['tutorial', 'how to', 'guide', 'learn', 'diy', 'step by step']):
            return 'tutorial'
        elif any(word in text for word in ['review', 'unboxing', 'test', 'comparison', 'vs']):
            return 'review'
        elif any(word in text for word in ['vlog', 'daily', 'routine', 'day in', 'morning', 'skincare']):
            return 'vlog'
        elif any(word in text for word in ['music', 'song', 'cover', 'lyrics', 'dance']):
            return 'music'
        elif any(word in text for word in ['comedy', 'funny', 'prank', 'challenge', 'reaction']):
            return 'entertainment'
        elif any(word in text for word in ['news', 'breaking', 'update', 'report']):
            return 'news'
        elif any(word in text for word in ['cooking', 'recipe', 'food', 'kitchen']):
            return 'cooking'
        elif any(word in text for word in ['workout', 'fitness', 'exercise', 'yoga']):
            return 'fitness'
        else:
            return 'general'

    def generate_contextual_description(self, scene_index, total_scenes, video_type, uploader, title):
        """Generate contextual descriptions based on video type and scene position"""
        
        # Common elements
        presenter_desc = f"The content creator"
        if 'woman' in title.lower() or 'girl' in title.lower():
            presenter_desc = "A woman"
        elif 'man' in title.lower() or 'guy' in title.lower():
            presenter_desc = "A man"
        
        # Position-based descriptions
        if scene_index == 0:
            # Opening scene
            if video_type == 'tutorial':
                return f"{presenter_desc} appears on screen, likely introducing themselves and the topic. They may be in a well-lit indoor setting, wearing casual clothing, and addressing the camera directly with a welcoming gesture."
            elif video_type == 'vlog':
                return f"{presenter_desc} greets the camera with a smile, possibly waving. They appear to be in their usual filming location, wearing their typical style, and beginning their introduction to today's content."
            elif video_type == 'review':
                return f"{presenter_desc} introduces the product or topic they'll be reviewing, likely holding or displaying the item. The setting appears organized, possibly with the product prominently featured."
            else:
                return f"{presenter_desc} appears on screen to begin the video, introducing the topic with engaging body language and clear speech directed at the audience."
        
        elif scene_index == total_scenes - 1:
            # Closing scene
            if video_type == 'tutorial':
                return f"{presenter_desc} concludes the tutorial, possibly showing the final result. They may be thanking viewers, asking for engagement (likes/comments), and suggesting related content."
            elif video_type == 'vlog':
                return f"{presenter_desc} wraps up their vlog, possibly reflecting on the day's events. They appear relaxed and are likely saying goodbye to viewers with a friendly gesture."
            else:
                return f"{presenter_desc} concludes the video with final thoughts, thanking viewers for watching, and encouraging engagement through likes, comments, and subscriptions."
        
        else:
            # Middle scenes - content-specific
            if video_type == 'tutorial':
                step_num = scene_index
                return f"{presenter_desc} demonstrates step {step_num} of the process, showing specific techniques and explaining the procedure. They may be using tools or materials, with close-up shots of their hands working."
            
            elif video_type == 'review':
                return f"{presenter_desc} examines different aspects of the product, pointing out features and sharing their opinions. They may be holding, using, or demonstrating the item while speaking to the camera."
            
            elif video_type == 'vlog':
                return f"{presenter_desc} continues sharing their experience, possibly showing different locations or activities. The scene captures candid moments with natural lighting and casual interactions."
            
            elif video_type == 'cooking':
                return f"{presenter_desc} works in the kitchen, preparing ingredients or cooking. They demonstrate techniques while explaining each step, with kitchen tools and ingredients visible on the counter."
            
            elif video_type == 'fitness':
                return f"{presenter_desc} demonstrates exercise movements, likely in workout attire in a gym or home setting. They show proper form while providing instruction and motivation."
            
            else:
                return f"{presenter_desc} continues with the main content, engaging with the audience through clear explanations and demonstrations. The setting remains consistent with good lighting and clear audio."

    def detect_video_type(self, title, description):
        """Detect video type based on title and description"""
        text = (title + " " + description).lower()
        
        if any(word in text for word in ['music', 'song', 'album', 'artist', 'band', 'lyrics']):
            return "🎵 Music Video"
        elif any(word in text for word in ['tutorial', 'how to', 'guide', 'learn', 'teaching']):
            return "📚 Tutorial/Educational"
        elif any(word in text for word in ['funny', 'comedy', 'entertainment', 'vlog', 'challenge']):
            return "🎭 Entertainment/Comedy"
        elif any(word in text for word in ['news', 'breaking', 'report', 'update']):
            return "📰 News/Information"
        elif any(word in text for word in ['review', 'unboxing', 'test', 'comparison']):
            return "⭐ Review/Unboxing"
        elif any(word in text for word in ['commercial', 'ad', 'brand', 'product']):
            return "📺 Commercial/Advertisement"
        else:
            return "🎬 General Content"

    def detect_background_music(self, video_info):
        """Detect background music style"""
        title = video_info.get('title', '').lower()
        description = video_info.get('description', '').lower()
        
        if any(word in title for word in ['music', 'song', 'soundtrack']):
            return "🎵 Original Music/Soundtrack - Primary audio content"
        elif any(word in title for word in ['commercial', 'ad', 'brand']):
            return "🎶 Upbeat Commercial Music - Designed to enhance brand appeal"
        elif any(word in title for word in ['tutorial', 'how to', 'guide']):
            return "🔇 Minimal/No Background Music - Focus on instruction"
        elif any(word in title for word in ['vlog', 'daily', 'life']):
            return "🎼 Ambient Background Music - Complementary to narration"
        else:
            return "🎵 Background Music - Complementing video mood and pacing"

    def detect_influencer_status(self, video_info):
        """Detect influencer status"""
        subscriber_count = video_info.get('channel_followers', 0)
        view_count = video_info.get('view_count', 0)
        
        if subscriber_count > 10000000:
            return "🌟 Mega Influencer (10M+ subscribers)"
        elif subscriber_count > 1000000:
            return "⭐ Major Influencer (1M+ subscribers)"
        elif subscriber_count > 100000:
            return "🎯 Mid-tier Influencer (100K+ subscribers)"
        elif subscriber_count > 10000:
            return "📈 Micro Influencer (10K+ subscribers)"
        elif view_count > 100000:
            return "🔥 Viral Content Creator"
        else:
            return "👤 Regular Content Creator"

    def format_number(self, num):
        if num is None or num == 0:
            return "0"
        if num >= 1_000_000_000:
            return f"{num/1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        return str(num)

    def format_video_info(self, video_info):
        """Compact video information formatting with tabular layout"""
        if not video_info:
            return "❌ No video information available."
    
        # Basic information
        title = video_info.get("title", "Unknown")
        uploader = video_info.get("uploader", "Unknown")
        duration = video_info.get("duration", 0)
        duration_str = f"{duration//60}:{duration%60:02d}" if duration else "Unknown"
        view_count = video_info.get("view_count", 0)
        like_count = video_info.get("like_count", 0)
        comment_count = video_info.get("comment_count", 0)
        upload_date = video_info.get("upload_date", "Unknown")
        
        # Format upload date
        if len(upload_date) == 8:
            formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
        else:
            formatted_date = upload_date
    
        # Generate enhanced analysis
        scene_descriptions = self.generate_scene_breakdown_gemini(video_info)
        scene_table_html = format_scene_breakdown(scene_descriptions)
        video_type = self.detect_video_type(title, video_info.get('description', ''))
        background_music = self.detect_background_music(video_info)
        influencer_status = self.detect_influencer_status(video_info)
        
        # Calculate engagement metrics
        engagement_rate = (like_count / view_count) * 100 if view_count > 0 else 0
        
        # Generate compact report with contrasting background
        report = f"""
    <div style='font-family: Arial, sans-serif; background: linear-gradient(135deg, #2d3748, #1a202c); padding: 20px; border-radius: 15px; border: 2px solid #FF8C00; box-shadow: 0 8px 32px rgba(255, 140, 0, 0.3);'>
    
        <div style='text-align: center; margin-bottom: 20px;'>
            <h2 style='color: #87CEEB; font-size: 24px; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>🎬 YouTube Video Analysis Report</h2>
            <div style='height: 3px; background: linear-gradient(90deg, #FF8C00, #87CEEB); margin: 10px 0; border-radius: 5px;'></div>
        </div>
    
        <!-- Compact Information Grid -->
        <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 20px;'>
            
            <!-- Basic Information Card -->
            <div style='background: rgba(135, 206, 235, 0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #87CEEB;'>
                <h3 style='color: #87CEEB; margin: 0 0 10px 0; font-size: 16px;'>📋 Basic Info</h3>
                <table style='width: 100%; font-size: 14px;'>
                    <tr><td style='color: #87CEEB; font-weight: bold; padding: 4px 0;'>📹 Title:</td></tr>
                    <tr><td style='color: #FFFFFF; padding: 4px 0 8px 0; word-wrap: wrap-word; white-space: normal; max-width: 200px;'>{title}</td></tr>
                    <tr><td style='color: #87CEEB; font-weight: bold; padding: 4px 0;'>👤 Creator:</td><td style='color: #87CEEB; padding: 2px 0;'>{uploader[:20]}{'...' if len(uploader) > 20 else ''}</td></tr>
                    <tr><td style='color: #87CEEB; font-weight: bold; padding: 4px 0;'>📅 Date:</td><td style='color: #87CEEB; padding: 2px 0;'>{formatted_date}</td></tr>
                    <tr><td style='color: #87CEEB; font-weight: bold; padding: 4px 0;'>⏱️ Duration:</td><td style='color: #87CEEB; padding: 2px 0;'>{duration_str}</td></tr>
                </table>
            </div>
    
            <!-- Performance Metrics Card -->
            <div style='background: rgba(135, 206, 235, 0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #FF8C00;border: 1px solid #444'>
                <h3 style='color: #87CEEB; margin: 0 0 10px 0; font-size: 16px;'>📊 Metrics</h3>
                <table style='width: 100%; font-size: 12px;'>
                    <tr><td style='color: #87CEEB; font-weight: bold; padding: 4px 0;'>👀 Views:</td><td style='color: #87CEEB; padding: 4px 0;'>{self.format_number(view_count)}</td></tr>
                    <tr><td style='color: #87CEEB; font-weight: bold; padding: 4px 0;'>👍 Likes:</td><td style='color: #87CEEB; padding: 4px 0;'>{self.format_number(like_count)}</td></tr>
                    <tr><td style='color: #87CEEB; font-weight: bold; padding: 4px 0;'>💬 Comments:</td><td style='color: #87CEEB; padding: 4px 0;'>{self.format_number(comment_count)}</td></tr>
                    <tr><td style='color: #87CEEB; font-weight: bold; padding: 4px 0;'>📈 Engagement:</td><td style='color: #87CEEB; padding: 4px 0;'>{engagement_rate:.2f}%</td></tr>
                </table>
            </div>
    
            <!-- Content Analysis Card -->
            <div style='background:rgba(135, 206, 235, 0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #87CEEB;border: 1px solid #444'>
                <h3 style='color:#87CEEB; margin: 0 0 10px 0; font-size: 16px;'>🎯 Analysis</h3>
                <table style='width: 100%; font-size: 12px;'>
                    <tr><td style='color: #87CEEB; font-weight: bold; padding: 4px 0;'>📂 Type:</td></tr>
                    <tr><td style='color: 87CEEB; padding: 4px 0 8px 0; word-break: break-word;'>{video_type}</td></tr>
                    <tr><td style='color: #87CEEB; font-weight: bold; padding: 4px 0;'>🎵 Music:</td></tr>
                    <tr><td style='color: #87CEEB; padding: 4px 0 8px 0; word-break: break-word;'>{background_music[:30]}{'...' if len(background_music) > 30 else ''}</td></tr>
                    <tr><td style='color: #87CEEB; font-weight: bold; padding: 4px 0;'>👑 Status:</td></tr>
                    <tr><td style='color: #87CEEB; padding: 4px 0; word-break: break-word;'>{influencer_status[:25]}{'...' if len(influencer_status) > 25 else ''}</td></tr>
                </table>
            </div>
        </div>
    
        <!-- Scene Breakdown Section -->
        <div style='background: rgba(0, 0, 0, 0.3); padding: 15px; border-radius: 10px; border: 1px solid #444;'>
            <h3 style='color: #87CEEB; margin: 0 0 15px 0; font-size: 18px; text-align: center;'>🎬 Scene-by-Scene Breakdown</h3>
            {scene_table_html}
        </div>
    
    </div>
    """
        
        return report.strip()
        
    def get_video_info(self, url, progress=gr.Progress(), cookiefile=None):
        """Extract video information"""
        if not url or not url.strip():
            return None, "❌ Please enter a YouTube URL"
        
        if not self.is_valid_youtube_url(url):
            return None, "❌ Invalid YouTube URL format"
        
        try:
            progress(0.1, desc="Initializing YouTube extractor...")
            
            ydl_opts = {
                'noplaylist': True,
                'extract_flat': False,
            }
            
            if cookiefile and os.path.exists(cookiefile):
                ydl_opts['cookiefile'] = cookiefile
            
            progress(0.5, desc="Extracting video metadata...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
            progress(1.0, desc="✅ Analysis complete!")
            
            return info, "✅ Video information extracted successfully"
            
        except Exception as e:
            return None, f"❌ Error: {str(e)}"

    def download_video(self, url, quality="best", audio_only=False, progress=gr.Progress(), cookiefile=None):
        """Download video with progress tracking"""
        if not url or not url.strip():
            return None, "❌ Please enter a YouTube URL"
        
        if not self.is_valid_youtube_url(url):
            return None, "❌ Invalid YouTube URL format"
        
        try:
            progress(0.1, desc="Preparing download...")
            
            # Create unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Download to temp directory first (Gradio compatible)
            ydl_opts = {
                'outtmpl': os.path.join(self.temp_downloads, f'%(title)s_{timestamp}.%(ext)s'),
                'noplaylist': True,
            }
            
            if audio_only:
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                if quality == "best":
                    ydl_opts['format'] = 'best[height<=1080]'
                elif quality == "720p":
                    ydl_opts['format'] = 'best[height<=720]'
                elif quality == "480p":
                    ydl_opts['format'] = 'best[height<=480]'
                else:
                    ydl_opts['format'] = 'best'
            
            if cookiefile and os.path.exists(cookiefile):
                ydl_opts['cookiefile'] = cookiefile
            
            # Progress hook
            def progress_hook(d):
                if d['status'] == 'downloading':
                    if 'total_bytes' in d:
                        percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        progress(0.1 + (percent / 100) * 0.7, desc=f"Downloading... {percent:.1f}%")
                    else:
                        progress(0.5, desc="Downloading...")
                elif d['status'] == 'finished':
                    progress(0.8, desc="Processing download...")
            
            ydl_opts['progress_hooks'] = [progress_hook]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
            progress(0.9, desc="Copying to Downloads folder...")
            
            # Find the downloaded file in temp directory
            downloaded_file_temp = None
            
            for file in os.listdir(self.temp_downloads):
                if timestamp in file:
                    downloaded_file_temp = os.path.join(self.temp_downloads, file)
                    break
            
            if not downloaded_file_temp:
                return None, "❌ Downloaded file not found in temp directory"
            
            # Copy to user's Downloads folder
            final_filename = os.path.basename(downloaded_file_temp)
            final_path = os.path.join(self.downloads_folder, final_filename)
            
            try:
                shutil.copy2(downloaded_file_temp, final_path)
                copy_success = True
            except Exception as e:
                print(f"Warning: Could not copy to Downloads folder: {e}")
                copy_success = False
                final_path = "File downloaded to temp location only"
            
            progress(1.0, desc="✅ Download complete!")
            
            success_msg = f"""✅ Download successful!
📁 Temp file (for download): {os.path.basename(downloaded_file_temp)}
📁 Permanent location: {final_path if copy_success else 'Copy failed'}
🎯 File size: {os.path.getsize(downloaded_file_temp) / (1024*1024):.1f} MB"""
            
            return downloaded_file_temp, success_msg
            
        except Exception as e:
            return None, f"❌ Download failed: {str(e)}"

# Initialize global downloader
downloader = YouTubeDownloader()

def configure_api_key(api_key):
    """Configure Gemini API key"""
    if not api_key or not api_key.strip():
        return "❌ Please enter a valid Google API key", gr.update(visible=False)
    
    success, message = downloader.configure_gemini(api_key.strip())
    
    if success:
        return message, gr.update(visible=True)
    else:
        return message, gr.update(visible=False)

def analyze_with_cookies(url, cookies_file, progress=gr.Progress()):
    """Main analysis function"""
    try:
        progress(0.05, desc="Starting analysis...")
        
        cookiefile = None
        if cookies_file and os.path.exists(cookies_file):
            cookiefile = cookies_file
        
        info, msg = downloader.get_video_info(url, progress=progress, cookiefile=cookiefile)
        
        if info:
            progress(0.95, desc="Generating comprehensive report...")
            formatted_info = downloader.format_video_info(info)
            progress(1.0, desc="✅ Complete!")
            return formatted_info
        else:
            return f"❌ Analysis Failed: {msg}"
            
    except Exception as e:
        return f"❌ System Error: {str(e)}"


def analyze_and_generate_pdf(url, cookies_file, progress=gr.Progress()):
    try:
        progress(0.1, desc="Extracting video info...")
        cookiefile = cookies_file if cookies_file and os.path.exists(cookies_file) else None

        info, _ = downloader.get_video_info(url, progress=progress, cookiefile=cookiefile)
        if not info:
            return "❌ Failed to extract video info"

        progress(0.6, desc="Generating HTML report...")
        report_html = downloader.format_video_info(info)

        progress(0.8, desc="Creating PDF...")

        # Generate PDF from HTML
        pdf_data = BytesIO()
        result = pisa.CreatePDF(report_html, dest=pdf_data)

        if result.err:
            return "❌ PDF generation failed"

        pdf_data.seek(0)
        pdf_path = os.path.join(tempfile.gettempdir(), f"analysis_report_{uuid.uuid4().hex}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_data.read())

        progress(1.0, desc="✅ PDF ready!")
        print("✅ PDF generated at:", pdf_path)
        return pdf_path  # ✅ Return direct path like in test code

    except Exception as e:
        print("❌ Exception:", e)
        return f"❌ Error: {str(e)}"

def generate_pdf_from_html(html_content):
    """Generate PDF with simplified HTML that works better with xhtml2pdf"""
    try:
        # Create a simplified version of the HTML for PDF generation
        # Remove complex CSS that xhtml2pdf can't handle
        simplified_html = html_content.replace(
            "background: linear-gradient(135deg, #2d3748, #1a202c);", 
            "background-color: #f5f5f5;"
        ).replace(
            "background: linear-gradient(90deg, #FF8C00, #87CEEB);", 
            "background-color: #FF8C00;"
        ).replace(
            "rgba(135, 206, 235, 0.1)", 
            "#f9f9f9"
        ).replace(
            "rgba(0, 0, 0, 0.3)", 
            "#ffffff"
        ).replace(
            "text-shadow: 2px 2px 4px rgba(0,0,0,0.5);", 
            ""
        ).replace(
            "box-shadow: 0 8px 32px rgba(255, 140, 0, 0.3);", 
            ""
        ).replace(
            "box-shadow: 0 4px 8px rgba(0,0,0,0.3);", 
            ""
        ).replace(
            "display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;", 
            "display: block;"
        ).replace(
            "background-color:#1a1a1a;", 
            "background-color:#ffffff;"
        ).replace(
            "color: #FFFFFF;", 
            "color: #000000;"
        ).replace(
            "background-color:#FF8C00; color: #000000;", 
            "background-color:#FF8C00; color: #000000;"
        ).replace(
            "color: #87CEEB;", 
            "color: #000080;"
        ).replace(
            "border: 2px solid #FF8C00;", 
            "border: 1px solid #FF8C00;"
        )
        
        # Remove table styling that causes issues
        simplified_html = re.sub(r"style='[^']*background-color:#1a1a1a[^']*'", "style='background-color:#ffffff;'", simplified_html)
        simplified_html = re.sub(r"style='[^']*color: #87CEEB[^']*'", "style='color: #000080; padding: 8px;'", simplified_html)
        
        # Wrap in a complete HTML document with PDF-friendly CSS
        pdf_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    size: A4;
                    margin: 1cm;
                }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    font-size: 12px;
                    line-height: 1.4;
                    color: #000000;
                    background-color: #ffffff;
                }}
                .report-container {{
                    background-color: #ffffff;
                    padding: 15px;
                    border: 2px solid #FF8C00;
                    border-radius: 8px;
                }}
                .header {{
                    text-align: center;
                    color: #FF8C00;
                    font-size: 20px;
                    font-weight: bold;
                    margin-bottom: 15px;
                    border-bottom: 2px solid #FF8C00;
                    padding-bottom: 8px;
                }}
                .info-card {{
                    background-color: #f9f9f9;
                    padding: 12px;
                    margin: 8px 0;
                    border-left: 3px solid #87CEEB;
                    border-radius: 4px;
                    page-break-inside: avoid;
                }}
                .info-title {{
                    color: #000080;
                    font-size: 14px;
                    font-weight: bold;
                    margin-bottom: 8px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 8px 0;
                    page-break-inside: avoid;
                }}
                th, td {{
                    padding: 6px 8px;
                    border: 1px solid #cccccc;
                    text-align: left;
                    vertical-align: top;
                    font-size: 11px;
                }}
                th {{
                    background-color: #FF8C00;
                    color: #000000;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .scene-table {{
                    margin-top: 15px;
                }}
                .scene-header {{
                    color: #000080;
                    font-size: 16px;
                    font-weight: bold;
                    text-align: center;
                    margin-bottom: 10px;
                }}
                div[style*="display: grid"] {{
                    display: block !important;
                }}
                div[style*="grid-template-columns"] > div {{
                    display: block !important;
                    margin-bottom: 10px !important;
                    width: 100% !important;
                }}
            </style>
        </head>
        <body>
            <div class="report-container">
                {simplified_html}
            </div>
        </body>
        </html>
        """
        
        result = BytesIO()
        pisa_status = pisa.CreatePDF(pdf_html, dest=result)
        
        if pisa_status.err:
            print(f"PDF generation error: {pisa_status.err}")
            return None
            
        result.seek(0)
        return result
        
    except Exception as e:
        print(f"PDF generation exception: {e}")
        return None



def download_with_cookies(url, quality, audio_only, cookies_file, progress=gr.Progress()):
    """Main download function"""
    try:
        progress(0.05, desc="Preparing download...")
        
        cookiefile = None
        if cookies_file and os.path.exists(cookies_file):
            cookiefile = cookies_file
        
        file_path, msg = downloader.download_video(url, quality, audio_only, progress=progress, cookiefile=cookiefile)
        
        if file_path:
            return file_path, msg
        else:
            return None, msg
            
    except Exception as e:
        return None, f"❌ System Error: {str(e)}"

def create_interface():
    """Create and configure the Gradio interface"""
    with gr.Blocks(
          css="""
        /* Main dark theme background and text */
        .gradio-container, .app, body {
            background-color: #1a1a1a !important;
            color: #87CEEB !important;
            font-weight: bold !important;
        }
                /* 🔵 Dark blue overrides for key labels */
        h3, .gr-group h3, .gradio-container h3 {
            color: #87CEEB !important;
        }

        label, .gr-textbox label, .gr-file label, .gr-dropdown label, .gr-checkbox label {
            color: #00008B !important;
            font-weight: bold !important;
        }

        .gr-file .file-name {
            color: #00008B !important;
            font-weight: bold !important;
        }

        /* Make tab labels dark blue too */
        .gr-tab-nav button {
            color: #00008B !important;
        }

        .gr-tab-nav button.selected {
            background-color: #FF8C00 !important;
            color: #000000 !important;
        }

        /* Light blue text for API status */
        .light-blue-text textarea {
            color: #87CEEB !important;
            background-color: #2a2a2a !important;
        }
        .gr-file {
            background-color: #2a2a2a !important;
            border: 2px dashed #444 !important;
        }

        .gr-group, .gr-form, .gr-row {
            background-color: #1a1a1a !important;
            border: 1px solid #444 !important;
            border-radius: 10px;
            padding: 15px;
        }

    """,
        theme=gr.themes.Soft(),
        title="📊 YouTube Video Analyzer & Downloader"
    ) as demo:
        
        # API Key Configuration Section
        with gr.Group():
            gr.HTML("<h3>🔑 Google Gemini API Configuration</h3>")
            with gr.Row():
                api_key_input = gr.Textbox(
                    label="🔑 Google API Key",
                    placeholder="Enter your Google API Key for enhanced AI analysis...",
                    type="password",
                    value=""
                )
                configure_btn = gr.Button("🔧 Configure API", variant="secondary")
            
            api_status = gr.Textbox(
                label="API Status",
                value="❌ Gemini API not configured - Using fallback analysis",
                interactive=False,
                lines=1,
                elem_classes="light-blue-text"
            )
            
            # Main Interface (initially hidden until API is configured)
            main_interface = gr.Group(visible=False)
            
            with main_interface:
                with gr.Row():
                    url_input = gr.Textbox(
                        label="🔗 YouTube URL",
                        placeholder="Paste your YouTube video URL here...",
                        value=""
                    )
                    
                    cookies_input = gr.File(
                        label="🍪 Upload cookies.txt (Mandatory)",
                        file_types=[".txt"],
                        type="filepath"
                    )
                
                with gr.Tabs():
                    with gr.TabItem("📊 Video Analysis"):
                        analyze_btn = gr.Button("🔍 Analyze Video", variant="primary")
                        
                        analysis_output = gr.HTML(
                            label="📊 Analysis Report",
                        )
                        download_pdf_btn = gr.Button("📄 Download Report as PDF", variant="secondary")
                        pdf_file_output = gr.File(label="📥 PDF Report", visible=True,interactive=False)

                    analyze_btn.click(
                        fn=analyze_with_cookies,
                        inputs=[url_input, cookies_input],
                        outputs=analysis_output,
                        show_progress=True
                    )
                    download_pdf_btn.click(
                        fn=analyze_and_generate_pdf,
                        inputs=[url_input, cookies_input],
                        outputs=pdf_file_output,
                        show_progress=True
                    )
                                                      
                    
                    with gr.TabItem("⬇️ Video Download"):
                        with gr.Row():
                            quality_dropdown = gr.Dropdown(
                                choices=["best", "720p", "480p"],
                                value="best",
                                label="📺 Video Quality"
                            )
                            
                            audio_only_checkbox = gr.Checkbox(
                                label="🎵 Audio Only (MP3)",
                                value=False
                            )
                        
                        download_btn = gr.Button("⬇️ Download Video", variant="primary")
                        
                        download_status = gr.Textbox(
                            label="📥 Download Status",
                            lines=5,
                            show_copy_button=True
                        )
                        
                        download_file = gr.File(
                            label="📁 Downloaded File",
                            visible=False
                        )
                        
                        def download_and_update(url, quality, audio_only, cookies_file, progress=gr.Progress()):
                            file_path, status = download_with_cookies(url, quality, audio_only, cookies_file, progress)
                            if file_path and os.path.exists(file_path):
                                return status, gr.update(value=file_path, visible=True)
                            else:
                                return status, gr.update(visible=False)
                        
                        download_btn.click(
                            fn=download_and_update,
                            inputs=[url_input, quality_dropdown, audio_only_checkbox, cookies_input],
                            outputs=[download_status, download_file],
                            show_progress=True
                        )
            
            # Configure API key button action
            configure_btn.click(
                fn=configure_api_key,
                inputs=[api_key_input],
                outputs=[api_status, main_interface]
            )
            
            # Always show interface option (for fallback mode)
            with gr.Row():
                show_interface_btn = gr.Button("🚀 Use Without Gemini API (Fallback Mode)", variant="secondary")
                
                def show_fallback_interface():
                    return "⚠️ Using fallback analysis mode", gr.update(visible=True)
                
                show_interface_btn.click(
                    fn=show_fallback_interface,
                    outputs=[api_status, main_interface]
                )
            
            gr.HTML("""
            <div style="margin-top: 20px; padding: 15px; background-color: #2a2a2a; border-radius: 10px; border-left: 5px solid #FF8C00; color: #87CEEB !important;">
                <h3 style="color: #87CEEB !important; font-weight: bold;">🔑 How to Get Google API Key:</h3>
                <ol style="color: #87CEEB !important; font-weight: bold;">
                    <li style="color: #87CEEB !important;">Go to <a href="https://console.cloud.google.com/" target="_blank" style="color: #87CEEB !important;">Google Cloud Console</a></li>
                    <li style="color: #87CEEB !important;">Create a new project or select an existing one</li>
                    <li style="color: #87CEEB !important;">Enable the "Generative Language API"</li>
                    <li style="color: #87CEEB !important;">Go to "Credentials" and create an API key</li>
                    <li style="color: #87CEEB !important;">Copy the API key and paste it above</li>
                </ol>
                <h3 style="color: #87CEEB !important; font-weight: bold;">✨ Benefits of using Gemini API:</h3>
                <ul style="color: #87CEEB !important; font-weight: bold;">
                    <li style="color: #87CEEB !important;">🤖 AI-powered scene descriptions with contextual understanding</li>
                    <li style="color: #87CEEB !important;">🎯 More accurate content type detection</li>
                    <li style="color: #87CEEB !important;">📊 Enhanced analysis based on video content</li>
                    <li style="color: #87CEEB !important;">⏰ Intelligent timestamp segmentation</li>
                </ul>
            </div>
            """)
    
    return demo
if __name__ == "__main__":
    demo = create_interface()
    import atexit
    atexit.register(downloader.cleanup)
    demo.launch(debug=True, show_error=True)
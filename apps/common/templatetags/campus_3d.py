import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def campus_3d_visual(module_name, width=120, height=80):
    """
    Renders a unified, lightweight, modern 3D SVG illustration with soft rounded geometry,
    pastel gradients, and cyan/blue highlights.
    """
    m = module_name.lower().strip()

    if 'academic' in m or 'risk' in m:
        # 3D Graduation Cap with predictive analytics chart & AI shield
        svg = f'''
        <svg width="{width}" height="{height}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d">
          <defs>
            <linearGradient id="grad_cap_{width}" x1="20" y1="20" x2="140" y2="90" gradientUnits="userSpaceOnUse">
              <stop stop-color="#19C7F2"/>
              <stop offset="1" stop-color="#4F9CF9"/>
            </linearGradient>
            <linearGradient id="shield_grad_{width}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#7C83FD"/>
              <stop offset="1" stop-color="#19C7F2"/>
            </linearGradient>
            <filter id="shadow_cap_{width}" x="0" y="0" width="160" height="110" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
              <feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#19C7F2" flood-opacity="0.25"/>
            </filter>
          </defs>
          <path d="M80 18L135 44L80 70L25 44L80 18Z" fill="url(#grad_cap_{width})" filter="url(#shadow_cap_{width})"/>
          <path d="M50 56V78C50 88 80 94 80 94C80 94 110 88 110 78V56L80 70L50 56Z" fill="#3B82F6" opacity="0.85"/>
          <!-- AI Predictive Bars -->
          <rect x="35" y="80" width="8" height="18" rx="4" fill="#22C55E"/>
          <rect x="48" y="72" width="8" height="26" rx="4" fill="#19C7F2"/>
          <rect x="61" y="66" width="8" height="32" rx="4" fill="#7C83FD"/>
          <!-- AI Shield Badge -->
          <circle cx="125" cy="75" r="16" fill="url(#shield_grad_{width})"/>
          <path d="M125 67L133 71V77C133 82 125 85 125 85C125 85 117 82 117 77V71L125 67Z" fill="#FFFFFF"/>
        </svg>
        '''
    elif 'event' in m or 'workshop' in m:
        # 3D Calendar + Ticket + Presentation Mic
        svg = f'''
        <svg width="{width}" height="{height}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d">
          <defs>
            <linearGradient id="event_grad_{width}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#4F9CF9"/>
              <stop offset="1" stop-color="#7C83FD"/>
            </linearGradient>
            <filter id="event_shadow_{width}" x="0" y="0" width="160" height="110">
              <feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#4F9CF9" flood-opacity="0.22"/>
            </filter>
          </defs>
          <!-- 3D Calendar Plate -->
          <rect x="30" y="24" width="75" height="65" rx="14" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="2" filter="url(#event_shadow_{width})"/>
          <path d="M30 38C30 30 36 24 44 24H91C99 24 105 30 105 38V42H30V38Z" fill="url(#event_grad_{width})"/>
          <circle cx="48" cy="33" r="3" fill="#FFFFFF"/>
          <circle cx="87" cy="33" r="3" fill="#FFFFFF"/>
          <rect x="42" y="52" width="12" height="10" rx="3" fill="#E2E8F0"/>
          <rect x="62" y="52" width="12" height="10" rx="3" fill="#19C7F2"/>
          <rect x="82" y="52" width="12" height="10" rx="3" fill="#E2E8F0"/>
          <rect x="42" y="68" width="12" height="10" rx="3" fill="#7C83FD"/>
          <!-- 3D Ticket Badge -->
          <rect x="90" y="48" width="55" height="38" rx="8" fill="#19C7F2" transform="rotate(-10 90 48)"/>
          <circle cx="90" cy="65" r="5" fill="#FFFFFF" transform="rotate(-10 90 48)"/>
          <circle cx="145" cy="65" r="5" fill="#FFFFFF" transform="rotate(-10 90 48)"/>
          <path d="M102 58L108 72M114 56L120 70" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="2 2" transform="rotate(-10 90 48)"/>
        </svg>
        '''
    elif 'club' in m:
        # 3D Avatars & Collaboration Star Badge
        svg = f'''
        <svg width="{width}" height="{height}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d">
          <defs>
            <linearGradient id="club_grad1_{width}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#19C7F2"/>
              <stop offset="1" stop-color="#4F9CF9"/>
            </linearGradient>
            <linearGradient id="club_grad2_{width}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#7C83FD"/>
              <stop offset="1" stop-color="#C084FC"/>
            </linearGradient>
          </defs>
          <!-- 3D Student Avatars -->
          <circle cx="55" cy="40" r="16" fill="url(#club_grad1_{width})"/>
          <path d="M32 78C32 66 42 60 55 60C68 60 78 66 78 78V82H32V78Z" fill="url(#club_grad1_{width})" opacity="0.8"/>
          
          <circle cx="105" cy="42" r="15" fill="url(#club_grad2_{width})"/>
          <path d="M84 78C84 68 94 62 105 62C116 62 126 68 126 78V82H84V78Z" fill="url(#club_grad2_{width})" opacity="0.8"/>
          
          <circle cx="80" cy="32" r="18" fill="#FFFFFF" stroke="#19C7F2" stroke-width="3"/>
          <circle cx="80" cy="32" r="14" fill="url(#club_grad1_{width})"/>
          <path d="M55 76C55 64 66 57 80 57C94 57 105 64 105 76V82H55V76Z" fill="#0284C7"/>
          <!-- Star Badge -->
          <circle cx="125" cy="25" r="12" fill="#F59E0B"/>
          <path d="M125 18L127 23H132L128 26L130 31L125 28L120 31L122 26L118 23H123L125 18Z" fill="#FFFFFF"/>
        </svg>
        '''
    elif 'project' in m or 'team' in m:
        # 3D Puzzle Cubes & Connected Technology Nodes
        svg = f'''
        <svg width="{width}" height="{height}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d">
          <defs>
            <linearGradient id="proj_cube1_{width}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#19C7F2"/>
              <stop offset="1" stop-color="#0284C7"/>
            </linearGradient>
            <linearGradient id="proj_cube2_{width}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#7C83FD"/>
              <stop offset="1" stop-color="#4F9CF9"/>
            </linearGradient>
          </defs>
          <!-- Cube 1 Isometric -->
          <path d="M60 25L90 40L60 55L30 40L60 25Z" fill="#38BDF8"/>
          <path d="M30 40L60 55V85L30 70V40Z" fill="url(#proj_cube1_{width})"/>
          <path d="M60 55L90 40V70L60 85V55Z" fill="#0369A1"/>
          
          <!-- Cube 2 Connected -->
          <path d="M105 45L135 60L105 75L75 60L105 45Z" fill="#A5B4FC"/>
          <path d="M75 60L105 75V95L75 80V60Z" fill="url(#proj_cube2_{width})"/>
          <path d="M105 75L135 60V80L105 95V75Z" fill="#4338CA"/>
          
          <!-- Connecting AI Beam -->
          <path d="M60 55L105 65" stroke="#F59E0B" stroke-width="3" stroke-dasharray="3 3"/>
          <circle cx="82" cy="60" r="5" fill="#F59E0B"/>
        </svg>
        '''
    elif 'complaint' in m or 'grievance' in m:
        # 3D Document + AI Routing Arrows & Priority Tag
        svg = f'''
        <svg width="{width}" height="{height}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d">
          <defs>
            <linearGradient id="doc_grad_{width}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#FFFFFF"/>
              <stop offset="1" stop-color="#F1F5F9"/>
            </linearGradient>
            <linearGradient id="headset_grad_{width}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#19C7F2"/>
              <stop offset="1" stop-color="#7C83FD"/>
            </linearGradient>
          </defs>
          <rect x="40" y="20" width="60" height="75" rx="8" fill="url(#doc_grad_{width})" stroke="#CBD5E1" stroke-width="2"/>
          <rect x="52" y="34" width="36" height="4" rx="2" fill="#94A3B8"/>
          <rect x="52" y="44" width="28" height="4" rx="2" fill="#CBD5E1"/>
          <rect x="52" y="54" width="32" height="4" rx="2" fill="#CBD5E1"/>
          <!-- AI Priority Badge -->
          <rect x="75" y="70" width="48" height="20" rx="10" fill="#EF4444"/>
          <text x="83" y="84" fill="#FFFFFF" font-family="Inter" font-size="10" font-weight="700">HIGH</text>
          <!-- 3D AI Headset / Triage Node -->
          <circle cx="115" cy="38" r="16" fill="url(#headset_grad_{width})"/>
          <path d="M110 38L114 42L121 34" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        '''
    elif 'transport' in m or 'bus' in m:
        # 3D Isometric Campus Bus + GPS Route Pin
        svg = f'''
        <svg width="{width}" height="{height}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d">
          <defs>
            <linearGradient id="bus_grad_{width}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#19C7F2"/>
              <stop offset="1" stop-color="#0284C7"/>
            </linearGradient>
          </defs>
          <!-- Bus Body Isometric -->
          <path d="M50 35L110 50L75 75L15 60L50 35Z" fill="#38BDF8"/>
          <path d="M15 60L75 75V92L15 77V60Z" fill="url(#bus_grad_{width})"/>
          <path d="M75 75L110 50V68L75 92V75Z" fill="#0369A1"/>
          <!-- Windows -->
          <path d="M25 61L45 66V71L25 66V61Z" fill="#E0F2FE"/>
          <path d="M50 67L70 72V77L50 72V67Z" fill="#E0F2FE"/>
          <!-- Wheels -->
          <ellipse cx="35" cy="82" rx="7" ry="9" fill="#0F172A"/>
          <ellipse cx="65" cy="89" rx="7" ry="9" fill="#0F172A"/>
          <!-- 3D GPS Pin -->
          <path d="M125 22C125 15 131 10 137 10C143 10 149 15 149 22C149 31 137 42 137 42C137 42 125 31 125 22Z" fill="#EF4444"/>
          <circle cx="137" cy="22" r="4" fill="#FFFFFF"/>
        </svg>
        '''
    elif 'traffic' in m:
        # 3D Camera with Car & AI Detection Frame
        svg = f'''
        <svg width="{width}" height="{height}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d">
          <defs>
            <linearGradient id="cam_grad_{width}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#4F9CF9"/>
              <stop offset="1" stop-color="#19C7F2"/>
            </linearGradient>
          </defs>
          <rect x="30" y="30" width="55" height="42" rx="8" fill="url(#cam_grad_{width})"/>
          <circle cx="57" cy="51" r="14" fill="#FFFFFF"/>
          <circle cx="57" cy="51" r="9" fill="#0F172A"/>
          <!-- AI Bounding Box -->
          <rect x="90" y="35" width="50" height="45" rx="6" fill="none" stroke="#22C55E" stroke-width="2" stroke-dasharray="4 2"/>
          <path d="M100 65L115 55L130 65H100Z" fill="#3B82F6"/>
          <circle cx="106" cy="67" r="4" fill="#0F172A"/>
          <circle cx="124" cy="67" r="4" fill="#0F172A"/>
          <rect x="92" y="27" width="36" height="12" rx="3" fill="#22C55E"/>
          <text x="96" y="36" fill="#FFFFFF" font-family="Inter" font-size="8" font-weight="700">CAR: 98%</text>
        </svg>
        '''
    elif 'parking' in m:
        # 3D Parking Structure + 'P' Badge + Available Bays
        svg = f'''
        <svg width="{width}" height="{height}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d">
          <defs>
            <linearGradient id="park_grad_{width}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#19C7F2"/>
              <stop offset="1" stop-color="#4F9CF9"/>
            </linearGradient>
          </defs>
          <!-- Ground Bays Isometric -->
          <path d="M80 30L140 60L80 90L20 60L80 30Z" fill="#F1F5F9" stroke="#CBD5E1" stroke-width="2"/>
          <!-- Bay Dividers -->
          <path d="M60 40L100 60M40 50L80 70" stroke="#94A3B8" stroke-width="2" stroke-dasharray="4 3"/>
          <!-- Parked 3D Car -->
          <rect x="65" y="52" width="26" height="16" rx="5" fill="#3B82F6" transform="rotate(25 65 52)"/>
          <!-- 3D 'P' Marker Beacon -->
          <circle cx="115" cy="30" r="16" fill="url(#park_grad_{width})"/>
          <text x="110" y="37" fill="#FFFFFF" font-family="Outfit" font-size="18" font-weight="800">P</text>
          <circle cx="127" cy="18" r="5" fill="#22C55E"/>
        </svg>
        '''
    elif 'canteen' in m or 'food' in m:
        # 3D Meal Tray + Cloche + Eco Leaf
        svg = f'''
        <svg width="{width}" height="{height}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d">
          <defs>
            <linearGradient id="food_grad_{width}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#F59E0B"/>
              <stop offset="1" stop-color="#FB923C"/>
            </linearGradient>
          </defs>
          <ellipse cx="80" cy="75" rx="55" ry="18" fill="#E2E8F0"/>
          <ellipse cx="80" cy="72" rx="50" ry="15" fill="#FFFFFF"/>
          <!-- Cloche Dome -->
          <path d="M45 68C45 42 60 32 80 32C100 32 115 42 115 68H45Z" fill="url(#food_grad_{width})"/>
          <circle cx="80" cy="27" r="6" fill="#D97706"/>
          <!-- Green Eco Leaf (Waste Reduction) -->
          <path d="M115 35C115 35 130 35 135 48C135 48 122 52 115 35Z" fill="#22C55E"/>
        </svg>
        '''
    elif 'waste' in m or 'segregation' in m:
        # 3D Recycling Bins + AI Vision Scanner
        svg = f'''
        <svg width="{width}" height="{height}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d">
          <!-- Bin 1 (Blue) -->
          <path d="M30 45L40 38H65L75 45L70 85H35L30 45Z" fill="#3B82F6"/>
          <ellipse cx="52" cy="42" rx="20" ry="5" fill="#60A5FA"/>
          <!-- Bin 2 (Green) -->
          <path d="M85 45L95 38H120L130 45L125 85H90L85 45Z" fill="#22C55E"/>
          <ellipse cx="107" cy="42" rx="20" ry="5" fill="#4ADE80"/>
          <!-- AI Laser Scan -->
          <path d="M20 30L140 30" stroke="#19C7F2" stroke-width="2" stroke-dasharray="3 3"/>
          <circle cx="80" cy="30" r="5" fill="#19C7F2"/>
        </svg>
        '''
    elif 'energy' in m or 'electricity' in m:
        # 3D Building + Lightning Bolt + Gauge
        svg = f'''
        <svg width="{width}" height="{height}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d">
          <defs>
            <linearGradient id="energy_bolt_{width}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#FACC15"/>
              <stop offset="1" stop-color="#F59E0B"/>
            </linearGradient>
          </defs>
          <!-- 3D Campus Sub-station -->
          <path d="M40 35L80 20L120 35V85L80 100L40 85V35Z" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="2"/>
          <path d="M80 20V100" stroke="#CBD5E1" stroke-width="1.5"/>
          <!-- Floating Electric Bolt -->
          <path d="M85 25L70 52H88L75 82L102 48H84L94 25H85Z" fill="url(#energy_bolt_{width})"/>
        </svg>
        '''
    elif 'department' in m:
        # 3D University Pillars + AI Brain Network
        svg = f'''
        <svg width="{width}" height="{height}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d">
          <path d="M80 15L135 38H25L80 15Z" fill="#19C7F2"/>
          <rect x="35" y="42" width="10" height="42" rx="3" fill="#64748B"/>
          <rect x="65" y="42" width="10" height="42" rx="3" fill="#64748B"/>
          <rect x="95" y="42" width="10" height="42" rx="3" fill="#64748B"/>
          <rect x="120" y="42" width="10" height="42" rx="3" fill="#64748B"/>
          <rect x="20" y="86" width="125" height="8" rx="2" fill="#334155"/>
          <!-- AI Brain Network Overlay -->
          <circle cx="80" cy="55" r="8" fill="#7C83FD"/>
          <path d="M80 55L40 60M80 55L125 60M80 55L70 75M80 55L95 75" stroke="#7C83FD" stroke-width="1.5"/>
        </svg>
        '''
    elif 'recommendation' in m:
        # 3D Neural Brain with floating stars and connected cards
        svg = f'''
        <svg width="{width}" height="{height}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d">
          <circle cx="80" cy="55" r="28" fill="url(#brand_grad_rec_{width})"/>
          <defs>
            <linearGradient id="brand_grad_rec_{width}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#19C7F2"/>
              <stop offset="1" stop-color="#7C83FD"/>
            </linearGradient>
          </defs>
          <!-- Glowing Connection Nodes -->
          <circle cx="45" cy="35" r="7" fill="#F59E0B"/>
          <circle cx="115" cy="35" r="7" fill="#22C55E"/>
          <circle cx="50" cy="80" r="7" fill="#4F9CF9"/>
          <circle cx="110" cy="80" r="7" fill="#A855F7"/>
          <path d="M80 55L45 35M80 55L115 35M80 55L50 80M80 55L110 80" stroke="#CBD5E1" stroke-width="2" stroke-dasharray="2 2"/>
        </svg>
        '''
    elif 'career' in m:
        # 3D Graduation Cap + Briefcase & Pathway
        svg = f'''
        <svg width="{width}" height="{height}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d">
          <rect x="40" y="45" width="55" height="40" rx="8" fill="#475569"/>
          <rect x="60" y="38" width="16" height="8" rx="2" stroke="#475569" stroke-width="2" fill="none"/>
          <path d="M100 25L135 40L100 55L65 40L100 25Z" fill="#19C7F2"/>
          <circle cx="120" cy="80" r="14" fill="#22C55E"/>
          <path d="M115 80L119 84L127 76" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        '''
    elif 'ai_mascot' in m or 'mascot' in m:
        # Friendly 3D AI Orb with concentric pulse rings
        svg = f'''
        <svg width="{width}" height="{height}" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg" class="ai-orb-svg">
          <circle cx="60" cy="60" r="48" fill="url(#mascot_glow_{width})" opacity="0.2"/>
          <circle cx="60" cy="60" r="38" fill="url(#mascot_sphere_{width})" filter="drop-shadow(0 6px 16px rgba(25, 199, 242, 0.4))"/>
          <!-- Mascot Eyes (Friendly AI) -->
          <ellipse cx="50" cy="56" rx="4" ry="6" fill="#FFFFFF"/>
          <ellipse cx="70" cy="56" rx="4" ry="6" fill="#FFFFFF"/>
          <ellipse cx="51" cy="55" rx="1.5" ry="2.5" fill="#0284C7"/>
          <ellipse cx="71" cy="55" rx="1.5" ry="2.5" fill="#0284C7"/>
          <path d="M55 68C58 71 62 71 65 68" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
          <defs>
            <radialGradient id="mascot_sphere_{width}" cx="0.35" cy="0.35" r="0.75">
              <stop stop-color="#38BDF8"/>
              <stop offset="0.7" stop-color="#0284C7"/>
              <stop offset="1" stop-color="#0369A1"/>
            </radialGradient>
            <radialGradient id="mascot_glow_{width}">
              <stop stop-color="#19C7F2"/>
              <stop offset="1" stop-color="transparent"/>
            </radialGradient>
          </defs>
        </svg>
        '''
    else:
        # Default AI Core Node
        svg = f'''
        <svg width="{width}" height="{height}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="80" cy="55" r="32" fill="#19C7F2" opacity="0.15"/>
          <circle cx="80" cy="55" r="22" fill="#19C7F2"/>
          <circle cx="80" cy="55" r="10" fill="#FFFFFF"/>
        </svg>
        '''

    return mark_safe(svg)

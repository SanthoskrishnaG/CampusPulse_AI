import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def campus_3d_visual(module_name, width=120, height=80):
    """
    Renders a unified, lightweight, modern 3D SVG illustration with soft rounded geometry,
    pastel gradients, and cyan/blue highlights.
    Visual family: #19C7F2 (Cyan), #4F9CF9 (Blue), #7C83FD (Accent), #F8FAFC, #0F172A.
    """
    m = module_name.lower().strip()
    w = width
    h = height

    if 'academic' in m or 'risk' in m:
        # 1. 3D Graduation Cap with predictive analytics chart & AI shield
        svg = f'''
        <svg width="{w}" height="{h}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d float-subtle">
          <defs>
            <linearGradient id="grad_cap_{w}" x1="20" y1="20" x2="140" y2="90" gradientUnits="userSpaceOnUse">
              <stop stop-color="#19C7F2"/>
              <stop offset="1" stop-color="#4F9CF9"/>
            </linearGradient>
            <linearGradient id="shield_grad_{w}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#7C83FD"/>
              <stop offset="1" stop-color="#19C7F2"/>
            </linearGradient>
            <filter id="shadow_cap_{w}" x="0" y="0" width="160" height="110" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
              <feDropShadow dx="0" dy="8" stdDeviation="6" flood-color="#19C7F2" flood-opacity="0.25"/>
            </filter>
          </defs>
          <!-- 3D Cap Rhombus -->
          <path d="M80 18L135 44L80 70L25 44L80 18Z" fill="url(#grad_cap_{w})" filter="url(#shadow_cap_{w})"/>
          <!-- Cap Skull Underside -->
          <path d="M50 56V78C50 88 80 94 80 94C80 94 110 88 110 78V56L80 70L50 56Z" fill="#3B82F6" opacity="0.88"/>
          <!-- Tassel -->
          <path d="M80 44C105 48 112 60 116 76" stroke="#F59E0B" stroke-width="2.5" stroke-linecap="round"/>
          <circle cx="116" cy="78" r="3.5" fill="#F59E0B"/>
          <!-- 3D Predictive Analytics Bars -->
          <rect x="35" y="80" width="9" height="20" rx="4.5" fill="#22C55E"/>
          <rect x="48" y="70" width="9" height="30" rx="4.5" fill="#19C7F2"/>
          <rect x="61" y="62" width="9" height="38" rx="4.5" fill="#7C83FD"/>
          <!-- AI Shield Badge -->
          <circle cx="126" cy="74" r="16" fill="url(#shield_grad_{w})" filter="url(#shadow_cap_{w})"/>
          <path d="M126 66L134 70V76C134 81 126 84 126 84C126 84 118 81 118 76V70L126 66Z" fill="#FFFFFF"/>
          <path d="M123 75L125.5 77.5L129.5 72.5" stroke="#19C7F2" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        '''
    elif 'event' in m or 'workshop' in m:
        # 2. 3D Calendar + Ticket + Presentation Mic
        svg = f'''
        <svg width="{w}" height="{h}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d float-subtle">
          <defs>
            <linearGradient id="event_grad_{w}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#4F9CF9"/>
              <stop offset="1" stop-color="#7C83FD"/>
            </linearGradient>
            <filter id="event_shadow_{w}" x="0" y="0" width="160" height="110">
              <feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#4F9CF9" flood-opacity="0.22"/>
            </filter>
          </defs>
          <!-- 3D Calendar Plate -->
          <rect x="28" y="22" width="78" height="68" rx="14" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="2" filter="url(#event_shadow_{w})"/>
          <path d="M28 38C28 29.16 35.16 22 44 22H90C98.84 22 106 29.16 106 38V42H28V38Z" fill="url(#event_grad_{w})"/>
          <circle cx="48" cy="32" r="3.5" fill="#FFFFFF"/>
          <circle cx="86" cy="32" r="3.5" fill="#FFFFFF"/>
          <!-- Calendar Day Grid -->
          <rect x="40" y="52" width="12" height="10" rx="3" fill="#E2E8F0"/>
          <rect x="61" y="52" width="12" height="10" rx="3" fill="#19C7F2"/>
          <rect x="82" y="52" width="12" height="10" rx="3" fill="#E2E8F0"/>
          <rect x="40" y="68" width="12" height="10" rx="3" fill="#7C83FD"/>
          <rect x="61" y="68" width="12" height="10" rx="3" fill="#22C55E"/>
          <!-- 3D Floating Ticket Badge -->
          <rect x="92" y="46" width="58" height="38" rx="9" fill="#19C7F2" transform="rotate(-12 92 46)"/>
          <circle cx="92" cy="65" r="5" fill="#FFFFFF" transform="rotate(-12 92 46)"/>
          <circle cx="150" cy="65" r="5" fill="#FFFFFF" transform="rotate(-12 92 46)"/>
          <path d="M106 56L112 72M118 54L124 70" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="2 2" transform="rotate(-12 92 46)"/>
        </svg>
        '''
    elif 'club' in m:
        # 3. 3D Group of Students + Club Badge + Collaboration
        svg = f'''
        <svg width="{w}" height="{h}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d float-subtle">
          <defs>
            <linearGradient id="club_grad1_{w}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#19C7F2"/>
              <stop offset="1" stop-color="#4F9CF9"/>
            </linearGradient>
            <linearGradient id="club_grad2_{w}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#7C83FD"/>
              <stop offset="1" stop-color="#C084FC"/>
            </linearGradient>
          </defs>
          <!-- Left Avatar -->
          <circle cx="52" cy="40" r="16" fill="url(#club_grad1_{w})"/>
          <path d="M30 80C30 67 40 61 52 61C64 61 74 67 74 80V84H30V80Z" fill="url(#club_grad1_{w})" opacity="0.82"/>
          <!-- Right Avatar -->
          <circle cx="108" cy="42" r="15" fill="url(#club_grad2_{w})"/>
          <path d="M86 80C86 69 96 63 108 63C120 63 130 69 130 80V84H86V80Z" fill="url(#club_grad2_{w})" opacity="0.82"/>
          <!-- Center Lead Avatar -->
          <circle cx="80" cy="32" r="18" fill="#FFFFFF" stroke="#19C7F2" stroke-width="3"/>
          <circle cx="80" cy="32" r="14" fill="url(#club_grad1_{w})"/>
          <path d="M54 77C54 64 66 57 80 57C94 57 106 64 106 77V84H54V77Z" fill="#0284C7"/>
          <!-- Star Achievement Badge -->
          <circle cx="128" cy="24" r="13" fill="#F59E0B" filter="drop-shadow(0 2px 4px rgba(245,158,11,0.4))"/>
          <path d="M128 17L130.5 22.5H136L131.5 26L133.5 31.5L128 28L122.5 31.5L124.5 26L120 22.5H125.5L128 17Z" fill="#FFFFFF"/>
        </svg>
        '''
    elif 'project' in m or 'team' in m:
        # 4. 3D Team + Project Board + Connected Nodes
        svg = f'''
        <svg width="{w}" height="{h}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d float-subtle">
          <defs>
            <linearGradient id="proj_cube1_{w}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#19C7F2"/>
              <stop offset="1" stop-color="#0284C7"/>
            </linearGradient>
            <linearGradient id="proj_cube2_{w}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#7C83FD"/>
              <stop offset="1" stop-color="#4F9CF9"/>
            </linearGradient>
          </defs>
          <!-- Isometric Cube 1 -->
          <path d="M58 24L88 39L58 54L28 39L58 24Z" fill="#38BDF8"/>
          <path d="M28 39L58 54V86L28 71V39Z" fill="url(#proj_cube1_{w})"/>
          <path d="M58 54L88 39V71L58 86V54Z" fill="#0369A1"/>
          <!-- Isometric Cube 2 -->
          <path d="M106 44L136 59L106 74L76 59L106 44Z" fill="#A5B4FC"/>
          <path d="M76 59L106 74V96L76 81V59Z" fill="url(#proj_cube2_{w})"/>
          <path d="M106 74L136 59V81L106 96V74Z" fill="#4338CA"/>
          <!-- AI Connecting Bridge -->
          <path d="M58 54L106 66" stroke="#F59E0B" stroke-width="3.5" stroke-dasharray="4 3"/>
          <circle cx="82" cy="60" r="6" fill="#F59E0B"/>
          <circle cx="82" cy="60" r="2.5" fill="#FFFFFF"/>
        </svg>
        '''
    elif 'complaint' in m or 'grievance' in m:
        # 5. 3D Document + AI Routing Arrows + Triage Support
        svg = f'''
        <svg width="{w}" height="{h}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d float-subtle">
          <defs>
            <linearGradient id="doc_grad_{w}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#FFFFFF"/>
              <stop offset="1" stop-color="#F1F5F9"/>
            </linearGradient>
            <linearGradient id="headset_grad_{w}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#19C7F2"/>
              <stop offset="1" stop-color="#7C83FD"/>
            </linearGradient>
          </defs>
          <!-- 3D Document Paper -->
          <rect x="38" y="18" width="64" height="78" rx="8" fill="url(#doc_grad_{w})" stroke="#CBD5E1" stroke-width="2"/>
          <rect x="50" y="32" width="40" height="4" rx="2" fill="#94A3B8"/>
          <rect x="50" y="42" width="30" height="4" rx="2" fill="#CBD5E1"/>
          <rect x="50" y="52" width="36" height="4" rx="2" fill="#CBD5E1"/>
          <!-- NLP Priority Pill -->
          <rect x="74" y="68" width="52" height="22" rx="11" fill="#EF4444"/>
          <text x="83" y="83" fill="#FFFFFF" font-family="Inter, sans-serif" font-size="10" font-weight="700">AI HIGH</text>
          <!-- 3D AI Support Node -->
          <circle cx="118" cy="36" r="17" fill="url(#headset_grad_{w})"/>
          <path d="M112 36L116 40L124 32" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        '''
    elif 'transport' in m or 'bus' in m:
        # 6. 3D Campus Bus + GPS + Route
        svg = f'''
        <svg width="{w}" height="{h}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d float-subtle">
          <defs>
            <linearGradient id="bus_grad_{w}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#19C7F2"/>
              <stop offset="1" stop-color="#0284C7"/>
            </linearGradient>
          </defs>
          <!-- Bus Isometric Body -->
          <path d="M52 32L115 48L78 74L15 58L52 32Z" fill="#38BDF8"/>
          <path d="M15 58L78 74V92L15 76V58Z" fill="url(#bus_grad_{w})"/>
          <path d="M78 74L115 48V66L78 92V74Z" fill="#0369A1"/>
          <!-- Windows -->
          <path d="M26 59L46 64V69L26 64V59Z" fill="#E0F2FE"/>
          <path d="M52 65L72 70V75L52 70V65Z" fill="#E0F2FE"/>
          <!-- Wheels -->
          <ellipse cx="36" cy="81" rx="7.5" ry="9.5" fill="#0F172A"/>
          <ellipse cx="67" cy="88" rx="7.5" ry="9.5" fill="#0F172A"/>
          <!-- 3D GPS Pin -->
          <path d="M128 20C128 13 134 8 140 8C146 8 152 13 152 20C152 29 140 40 140 40C140 40 128 29 128 20Z" fill="#EF4444"/>
          <circle cx="140" cy="20" r="4.5" fill="#FFFFFF"/>
        </svg>
        '''
    elif 'traffic' in m:
        # 7. 3D Camera + Vehicles + AI Bounding Box
        svg = f'''
        <svg width="{w}" height="{h}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d float-subtle">
          <defs>
            <linearGradient id="cam_grad_{w}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#4F9CF9"/>
              <stop offset="1" stop-color="#19C7F2"/>
            </linearGradient>
          </defs>
          <!-- Camera Body -->
          <rect x="28" y="28" width="58" height="44" rx="10" fill="url(#cam_grad_{w})"/>
          <circle cx="57" cy="50" r="15" fill="#FFFFFF"/>
          <circle cx="57" cy="50" r="9.5" fill="#0F172A"/>
          <circle cx="54" cy="47" r="3" fill="#38BDF8"/>
          <!-- AI Bounding Box Overlay -->
          <rect x="90" y="32" width="54" height="48" rx="6" fill="none" stroke="#22C55E" stroke-width="2.5" stroke-dasharray="4 2"/>
          <path d="M102 66L117 55L132 66H102Z" fill="#3B82F6"/>
          <circle cx="108" cy="68" r="4" fill="#0F172A"/>
          <circle cx="126" cy="68" r="4" fill="#0F172A"/>
          <rect x="92" y="24" width="40" height="13" rx="3" fill="#22C55E"/>
          <text x="96" y="34" fill="#FFFFFF" font-family="Inter, sans-serif" font-size="8" font-weight="700">CAR: 98%</text>
        </svg>
        '''
    elif 'parking' in m:
        # 8. 3D Cars + Parking Structure + 'P' Beacon
        svg = f'''
        <svg width="{w}" height="{h}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d float-subtle">
          <defs>
            <linearGradient id="park_grad_{w}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#19C7F2"/>
              <stop offset="1" stop-color="#4F9CF9"/>
            </linearGradient>
          </defs>
          <!-- Isometric Bays Ground -->
          <path d="M80 28L144 60L80 92L16 60L80 28Z" fill="#F1F5F9" stroke="#CBD5E1" stroke-width="2"/>
          <path d="M58 39L102 61M36 50L80 72" stroke="#94A3B8" stroke-width="2" stroke-dasharray="4 3"/>
          <!-- Parked 3D Car -->
          <rect x="66" y="52" width="28" height="17" rx="5" fill="#3B82F6" transform="rotate(25 66 52)"/>
          <ellipse cx="68" cy="67" rx="3" ry="2" fill="#0F172A"/>
          <ellipse cx="88" cy="57" rx="3" ry="2" fill="#0F172A"/>
          <!-- 3D 'P' Beacon -->
          <circle cx="120" cy="28" r="17" fill="url(#park_grad_{w})" filter="drop-shadow(0 4px 8px rgba(25,199,242,0.35))"/>
          <text x="114" y="36" fill="#FFFFFF" font-family="Outfit, sans-serif" font-size="20" font-weight="800">P</text>
          <circle cx="132" cy="16" r="5" fill="#22C55E"/>
        </svg>
        '''
    elif 'canteen' in m or 'food' in m:
        # 9. 3D Food Tray + Cloche + Eco Analytics Leaf
        svg = f'''
        <svg width="{w}" height="{h}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d float-subtle">
          <defs>
            <linearGradient id="food_grad_{w}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#F59E0B"/>
              <stop offset="1" stop-color="#FB923C"/>
            </linearGradient>
          </defs>
          <!-- Tray Plate -->
          <ellipse cx="80" cy="76" rx="58" ry="18" fill="#E2E8F0"/>
          <ellipse cx="80" cy="73" rx="52" ry="15" fill="#FFFFFF"/>
          <!-- 3D Cloche Dome -->
          <path d="M44 68C44 40 60 30 80 30C100 30 116 40 116 68H44Z" fill="url(#food_grad_{w})"/>
          <circle cx="80" cy="25" r="6" fill="#D97706"/>
          <!-- Eco Leaf (Waste Minimization) -->
          <path d="M118 34C118 34 134 34 139 48C139 48 125 52 118 34Z" fill="#22C55E"/>
          <!-- Analytics spark -->
          <circle cx="48" cy="38" r="4" fill="#19C7F2"/>
        </svg>
        '''
    elif 'waste' in m or 'segregation' in m:
        # 10. 3D Recycling Bins + AI Vision Laser Scanner
        svg = f'''
        <svg width="{w}" height="{h}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d float-subtle">
          <!-- Blue Bin (Recyclable) -->
          <path d="M28 46L38 38H64L74 46L68 88H34L28 46Z" fill="#3B82F6"/>
          <ellipse cx="51" cy="42" rx="21" ry="5.5" fill="#60A5FA"/>
          <path d="M47 58L51 54L55 58M51 55V68" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
          <!-- Green Bin (Organic) -->
          <path d="M86 46L96 38H122L132 46L126 88H92L86 46Z" fill="#22C55E"/>
          <ellipse cx="109" cy="42" rx="21" ry="5.5" fill="#4ADE80"/>
          <!-- AI Laser Scan Beam -->
          <path d="M18 30L142 30" stroke="#19C7F2" stroke-width="2.5" stroke-dasharray="3 3"/>
          <circle cx="80" cy="30" r="5" fill="#19C7F2"/>
        </svg>
        '''
    elif 'energy' in m or 'electricity' in m:
        # 11. 3D Campus Building + Solar/Lightning Bolt + Gauge
        svg = f'''
        <svg width="{w}" height="{h}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d float-subtle">
          <defs>
            <linearGradient id="energy_bolt_{w}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#FACC15"/>
              <stop offset="1" stop-color="#F59E0B"/>
            </linearGradient>
          </defs>
          <!-- 3D Substation Structure -->
          <path d="M38 35L80 18L122 35V85L80 102L38 85V35Z" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="2"/>
          <path d="M80 18V102" stroke="#CBD5E1" stroke-width="1.5"/>
          <!-- Floating Electric Bolt -->
          <path d="M86 24L70 52H88L74 84L104 48H86L96 24H86Z" fill="url(#energy_bolt_{w})" filter="drop-shadow(0 4px 10px rgba(245,158,11,0.4))"/>
        </svg>
        '''
    elif 'department' in m:
        # 12. 3D Academic Building + Analytics
        svg = f'''
        <svg width="{w}" height="{h}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d float-subtle">
          <path d="M80 14L138 38H22L80 14Z" fill="#19C7F2"/>
          <rect x="34" y="42" width="11" height="44" rx="3" fill="#64748B"/>
          <rect x="64" y="42" width="11" height="44" rx="3" fill="#64748B"/>
          <rect x="94" y="42" width="11" height="44" rx="3" fill="#64748B"/>
          <rect x="120" y="42" width="11" height="44" rx="3" fill="#64748B"/>
          <rect x="18" y="88" width="130" height="9" rx="2" fill="#334155"/>
          <!-- AI Brain Network Overlay -->
          <circle cx="80" cy="56" r="9" fill="#7C83FD"/>
          <path d="M80 56L39 60M80 56L126 60M80 56L70 76M80 56L96 76" stroke="#7C83FD" stroke-width="1.8"/>
        </svg>
        '''
    elif 'recommendation' in m:
        # 13. 3D AI Brain + Connected Recommendation Cards
        svg = f'''
        <svg width="{w}" height="{h}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d float-subtle">
          <defs>
            <linearGradient id="rec_grad_{w}" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#19C7F2"/>
              <stop offset="1" stop-color="#7C83FD"/>
            </linearGradient>
          </defs>
          <circle cx="80" cy="55" r="28" fill="url(#rec_grad_{w})" filter="drop-shadow(0 6px 14px rgba(25,199,242,0.3))"/>
          <!-- Connected Satellite Nodes -->
          <circle cx="42" cy="34" r="7" fill="#F59E0B"/>
          <circle cx="118" cy="34" r="7" fill="#22C55E"/>
          <circle cx="48" cy="82" r="7" fill="#4F9CF9"/>
          <circle cx="112" cy="82" r="7" fill="#A855F7"/>
          <path d="M80 55L42 34M80 55L118 34M80 55L48 82M80 55L112 82" stroke="#CBD5E1" stroke-width="2" stroke-dasharray="3 3"/>
        </svg>
        '''
    elif 'career' in m:
        # 14. 3D Graduation Cap + Career Path + Briefcase
        svg = f'''
        <svg width="{w}" height="{h}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d float-subtle">
          <rect x="38" y="44" width="58" height="42" rx="8" fill="#475569"/>
          <rect x="58" y="36" width="18" height="9" rx="2" stroke="#475569" stroke-width="2.5" fill="none"/>
          <path d="M102 22L138 38L102 54L66 38L102 22Z" fill="#19C7F2"/>
          <circle cx="122" cy="82" r="15" fill="#22C55E"/>
          <path d="M117 82L121 86L129 78" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        '''
    elif 'map' in m or 'campus' in m:
        # 15. 3D Isometric Campus Map
        svg = f'''
        <svg width="{w}" height="{h}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d float-subtle">
          <!-- Isometric Ground Grid -->
          <path d="M80 18L148 54L80 90L12 54L80 18Z" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="2"/>
          <path d="M46 36L114 72M80 18V90" stroke="#E2E8F0" stroke-width="1.5"/>
          <!-- Block 1 -->
          <path d="M60 38L80 48L60 58L40 48L60 38Z" fill="#38BDF8"/>
          <path d="M40 48L60 58V72L40 62V48Z" fill="#0284C7"/>
          <path d="M60 58L80 48V62L60 72V58Z" fill="#0369A1"/>
          <!-- Block 2 -->
          <path d="M100 52L120 62L100 72L80 62L100 52Z" fill="#A5B4FC"/>
          <path d="M80 62L100 72V84L80 74V62Z" fill="#7C83FD"/>
          <path d="M100 72L120 62V74L100 84V72Z" fill="#4338CA"/>
          <!-- Pin -->
          <circle cx="80" cy="32" r="6" fill="#EF4444"/>
        </svg>
        '''
    elif 'ai_mascot' in m or 'mascot' in m or 'assistant' in m or 'robot' in m:
        # 16. Friendly Premium 3D AI Robot / Orb
        svg = f'''
        <svg width="{w}" height="{h}" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg" class="visual-3d float-subtle">
          <defs>
            <radialGradient id="mascot_sphere_{w}" cx="0.35" cy="0.35" r="0.75">
              <stop stop-color="#38BDF8"/>
              <stop offset="0.7" stop-color="#0284C7"/>
              <stop offset="1" stop-color="#0369A1"/>
            </radialGradient>
            <radialGradient id="mascot_glow_{w}">
              <stop stop-color="#19C7F2"/>
              <stop offset="1" stop-color="transparent"/>
            </radialGradient>
          </defs>
          <circle cx="60" cy="60" r="48" fill="url(#mascot_glow_{w})" opacity="0.25"/>
          <circle cx="60" cy="60" r="38" fill="url(#mascot_sphere_{w})" filter="drop-shadow(0 8px 18px rgba(25, 199, 242, 0.4))"/>
          <!-- Friendly Mascot Eyes -->
          <ellipse cx="50" cy="56" rx="4.5" ry="6.5" fill="#FFFFFF"/>
          <ellipse cx="70" cy="56" rx="4.5" ry="6.5" fill="#FFFFFF"/>
          <ellipse cx="51.5" cy="55.5" rx="2" ry="3" fill="#0284C7"/>
          <ellipse cx="71.5" cy="55.5" rx="2" ry="3" fill="#0284C7"/>
          <!-- Friendly Smile -->
          <path d="M54 68C57.5 71.5 62.5 71.5 66 68" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"/>
          <!-- Antenna -->
          <path d="M60 22V14" stroke="#38BDF8" stroke-width="2.5" stroke-linecap="round"/>
          <circle cx="60" cy="12" r="4" fill="#19C7F2"/>
        </svg>
        '''
    else:
        # Default AI Core Node
        svg = f'''
        <svg width="{w}" height="{h}" viewBox="0 0 160 110" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="80" cy="55" r="32" fill="#19C7F2" opacity="0.15"/>
          <circle cx="80" cy="55" r="22" fill="#19C7F2"/>
          <circle cx="80" cy="55" r="10" fill="#FFFFFF"/>
        </svg>
        '''

    return mark_safe(svg)


@register.simple_tag
def ai_data_flow(data_label="Campus Data", model_label="ML/DL Model", pred_label="Prediction", rec_label="Recommendation", action_label="Action"):
    """
    Renders the standardized 5-step AI Data Flow stepper:
    DATA -> ML/DL MODEL -> PREDICTION -> RECOMMENDATION -> ACTION
    with animated pulses along connection paths.
    """
    html = f'''
    <div class="ai-data-flow-stepper" title="AI Intelligence Pipeline">
        <div class="flow-step">
            <span class="flow-step-icon">📊</span>
            <span class="flow-step-title">{data_label}</span>
            <span class="flow-step-sub">Telemetry</span>
        </div>
        <div class="flow-connector"><span class="flow-pulse"></span>➔</div>
        <div class="flow-step highlight-model">
            <span class="flow-step-icon">🧠</span>
            <span class="flow-step-title">{model_label}</span>
            <span class="flow-step-sub">AI Engine</span>
        </div>
        <div class="flow-connector"><span class="flow-pulse"></span>➔</div>
        <div class="flow-step">
            <span class="flow-step-icon">🎯</span>
            <span class="flow-step-title">{pred_label}</span>
            <span class="flow-step-sub">Inference</span>
        </div>
        <div class="flow-connector"><span class="flow-pulse"></span>➔</div>
        <div class="flow-step">
            <span class="flow-step-icon">💡</span>
            <span class="flow-step-title">{rec_label}</span>
            <span class="flow-step-sub">Guidance</span>
        </div>
        <div class="flow-connector"><span class="flow-pulse"></span>➔</div>
        <div class="flow-step highlight-action">
            <span class="flow-step-icon">⚡</span>
            <span class="flow-step-title">{action_label}</span>
            <span class="flow-step-sub">Intervention</span>
        </div>
    </div>
    '''
    return mark_safe(html)


@register.simple_tag
def ai_badge(badge_type="prediction", custom_text=None):
    """
    Renders unified AI visual badges:
    prediction, insight, recommendation, detected, forecast, classification, confidence, realtime, monitoring
    """
    bt = badge_type.lower().strip()
    badges = {
        'prediction': ('badge-ai-prediction', '✨ AI Prediction'),
        'insight': ('badge-ai-insight', '💡 AI Insight'),
        'recommendation': ('badge-ai-recommendation', '🎯 AI Recommendation'),
        'detected': ('badge-ai-detected', '👁️ AI Detected'),
        'forecast': ('badge-ai-forecast', '📈 AI Forecast'),
        'classification': ('badge-ai-classification', '🏷️ AI Classification'),
        'confidence': ('badge-ai-confidence', '⚡ AI Confidence'),
        'realtime': ('badge-ai-realtime', '● Real-Time AI'),
        'monitoring': ('badge-ai-monitoring', '🛡️ AI Monitoring'),
    }
    cls, default_text = badges.get(bt, ('badge-ai-prediction', '✨ AI'))
    text = custom_text if custom_text else default_text
    return mark_safe(f'<span class="ai-badge {cls}">{text}</span>')

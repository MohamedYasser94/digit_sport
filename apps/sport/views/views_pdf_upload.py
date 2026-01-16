"""
Enhanced PDF Upload View with JSON Preview and Real-time Progress
Shows extracted data in JSON format before saving to database
"""
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import os
import tempfile
import traceback

from apps.sport.models import MatchPlayerReport, PlayerStatics
from apps.sport.models.models import Match, Players, Teams
from apps.sport.utils.pdf_extractor import VolleyballPDFExtractor
from helper.decorators import authenticated_staf, staff_only
from helper.commonHelper import BACKEND_TEMPLATES


@authenticated_staf
@staff_only
def AdminMatchPlayerStaticPdfUpload(request, match_slug):
    """
    Enhanced view to upload PDF, extract JSON, preview data, and update player statistics.
    - Shows JSON preview before saving
    - Real-time extraction progress
    - Detailed error reporting
    - Validation of matches between PDF data and database
    """
    try:
        match = get_object_or_404(Match, slug=match_slug)
    except Match.DoesNotExist:
        messages.error(request, _("Match not found"), extra_tags='Players')
        return HttpResponseRedirect(reverse_lazy('sport:AdminMatchList'))

    extraction_data = None
    json_preview = None

    if request.method == "POST" and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']

        # Create temporary file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, pdf_file.name)

        try:
            # Save uploaded file
            with open(temp_path, 'wb+') as destination:
                for chunk in pdf_file.chunks():
                    destination.write(chunk)

            # Extract data from PDF to JSON
            extractor = VolleyballPDFExtractor(dpi=300)
            extraction_data = extractor.extract(temp_path)

            # Check for extraction errors
            if 'error' in extraction_data:
                messages.error(
                    request,
                    _("PDF Extraction Error: ") + extraction_data['error'],
                    extra_tags='Players'
                )
                context = {
                    'match': match,
                    'current_page': _('Upload PDF Statistics'),
                    'error': extraction_data['error'],
                    'log': extraction_data.get('log', [])
                }
                return render(request, f'{BACKEND_TEMPLATES}/sport/match/statics_pdf.html', context)

            # Check if data was extracted
            if not extraction_data.get('teams'):
                messages.warning(
                    request,
                    _("No players found in PDF. Please verify the PDF format and try again."),
                    extra_tags='Players'
                )
                context = {
                    'match': match,
                    'current_page': _('Upload PDF Statistics'),
                    'error': 'No data extracted',
                    'log': extraction_data.get('log', [])
                }
                return render(request, f'{BACKEND_TEMPLATES}/sport/match/statics_pdf.html', context)

            # Generate JSON preview
            json_preview = json.dumps(extraction_data, indent=2, ensure_ascii=False)

            # Check if user wants to confirm and save
            confirm_save = request.POST.get('confirm_save', False)

            if not confirm_save:
                # Show preview without saving
                messages.info(
                    request,
                    _(f"Preview: Found {extraction_data['total_players']} players in {len(extraction_data['teams'])} team(s). Review the data and confirm to save."),
                    extra_tags='Players'
                )
                context = {
                    'match': match,
                    'current_page': _('Upload PDF Statistics'),
                    'extraction_data': extraction_data,
                    'json_preview': json_preview,
                    'teams_count': len(extraction_data['teams']),
                    'players_count': extraction_data['total_players'],
                    'log': extraction_data.get('log', [])
                }
                return render(request, f'{BACKEND_TEMPLATES}/sport/match/statics_pdf.html', context)

            # Proceed with saving data to database
            updated_count = 0
            skipped_players = []
            errors = []

            with transaction.atomic():
                for team_data in extraction_data['teams']:
                    for player_data in team_data['players']:
                        try:
                            player_name = player_data['name']
                            player_number = player_data['number']
                            stats = player_data['stats']

                            # Search for player by name
                            player = Players.objects.filter(
                                name__icontains=player_name
                            ).first()

                            # Try matching by number if name not found
                            if not player and player_number:
                                player = Players.objects.filter(
                                    number=player_number,
                                    team__in=[match.team1, match.team2]
                                ).first()

                            if not player:
                                skipped_players.append({
                                    'name': player_name,
                                    'number': player_number,
                                    'reason': 'Player not found in database'
                                })
                                continue

                            # Prepare stats for database
                            defaults = {
                                'pts': stats.get('pts', 0),
                                'serve_total': stats.get('serve_total', 0),
                                'serve_err': stats.get('serve_err', 0),
                                'serve_ace': stats.get('serve_ace', 0),
                                'reception_total': stats.get('reception_total', 0),
                                'reception_err': stats.get('reception_err', 0),
                                'reception_exc': stats.get('reception_exc', 0),
                                'attack_total': stats.get('attack_total', 0),
                                'attack_err': stats.get('attack_err', 0),
                                'attack_att': stats.get('attack_blo', 0),
                                'attack_pts': stats.get('attack_pts', 0),
                                'block_pts': stats.get('block_pts', 0),
                                'static_type': 'General'
                            }

                            # Update MatchPlayerReport
                            MatchPlayerReport.objects.update_or_create(
                                player=player,
                                match=match,
                                defaults=defaults
                            )

                            # Update PlayerStatics (overall stats)
                            PlayerStatics.objects.update_or_create(
                                player=player,
                                defaults=defaults
                            )

                            updated_count += 1

                        except Exception as e:
                            errors.append({
                                'player': player_name,
                                'error': str(e)
                            })
                            continue

            # Build result message
            msg = _(f"✓ Successfully updated statistics for {updated_count} players")

            if skipped_players:
                msg += _(f"\n⚠ Skipped {len(skipped_players)} players not found in database:")
                for p in skipped_players[:5]:
                    msg += f"\n  • {p['name']} (#{p['number']})"
                if len(skipped_players) > 5:
                    msg += f"\n  ... and {len(skipped_players) - 5} more"

            if errors:
                msg += _(f"\n✕ {len(errors)} errors during processing")
                for e in errors[:3]:
                    msg += f"\n  • {e['player']}: {e['error']}"

            if updated_count > 0:
                messages.success(request, msg, extra_tags='Players')
            else:
                messages.warning(request, msg, extra_tags='Players')

            # Redirect to match details
            return HttpResponseRedirect(
                reverse_lazy('sport:AdminMatchDetails', kwargs={'slug': match_slug})
            )

        except Exception as e:
            messages.error(
                request,
                _("Error processing PDF: ") + str(e),
                extra_tags='Players'
            )
            traceback.print_exc()

            context = {
                'match': match,
                'current_page': _('Upload PDF Statistics'),
                'error': str(e)
            }
            return render(request, f'{BACKEND_TEMPLATES}/sport/match/statics_pdf.html', context)

        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass

    # GET request - show upload form
    context = {
        'match': match,
        'current_page': _('Upload PDF Statistics'),
        'extraction_data': extraction_data,
        'json_preview': json_preview,
    }
    return render(request, f'{BACKEND_TEMPLATES}/sport/match/statics_pdf.html', context)


@require_http_methods(["GET"])
@authenticated_staf
@staff_only
def AdminPdfExtractionProgress(request):
    """
    API endpoint to get real-time extraction progress.
    Could be enhanced for async processing.
    """
    return JsonResponse({
        'status': 'ready',
        'message': 'PDF extraction system ready'
    })

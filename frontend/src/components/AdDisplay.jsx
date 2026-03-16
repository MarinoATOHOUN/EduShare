import React, { useState, useEffect, useRef } from 'react';
import { X, ExternalLink, Phone, Mail, Info } from 'lucide-react';
import { adsAPI } from '../lib/api';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';

const AdDisplay = ({ triggerAction }) => {
    const [currentAd, setCurrentAd] = useState(null);
    const [isVisible, setIsVisible] = useState(false);
    const showTimeRef = useRef(null);

    useEffect(() => {
        const fetchAds = async () => {
            try {
                const data = await adsAPI.getActiveAds();
                const filteredAds = data.filter(ad => ad.trigger_action === triggerAction);

                if (filteredAds.length > 0) {
                    // Show a random ad from the filtered list
                    const randomAd = filteredAds[Math.floor(Math.random() * filteredAds.length)];

                    // Check if user has dismissed this ad recently
                    const dismissedAds = JSON.parse(localStorage.getItem('dismissed_ads') || '[]');

                    // For action-based triggers (download, upload, timer), we might want to show them more often
                    const isActionTrigger = ['on_download', 'on_upload', 'on_timer'].includes(triggerAction);

                    if (!dismissedAds.includes(randomAd.id) || isActionTrigger) {
                        setCurrentAd(randomAd);
                        // Delay showing only for on_load to not be too aggressive
                        const delay = triggerAction === 'on_load' ? 1500 : 0;

                        setTimeout(() => {
                            setIsVisible(true);
                            showTimeRef.current = Date.now();

                            // Record view interaction
                            adsAPI.recordInteraction(randomAd.id, 'view');

                            // Auto-hide logic
                            if (randomAd.duration > 0) {
                                setTimeout(() => {
                                    if (isVisible) handleClose();
                                }, randomAd.duration * 1000);
                            }
                        }, delay);
                    }
                }
            } catch (error) {
                console.error('Error fetching ads:', error);
            }
        };

        fetchAds();
    }, [triggerAction]);

    const handleClose = () => {
        if (!isVisible) return;

        setIsVisible(false);
        const timeSpent = showTimeRef.current ? (Date.now() - showTimeRef.current) / 1000 : null;

        if (currentAd) {
            // Record close interaction with time spent
            adsAPI.recordInteraction(currentAd.id, 'close', timeSpent);

            const dismissedAds = JSON.parse(localStorage.getItem('dismissed_ads') || '[]');
            if (!dismissedAds.includes(currentAd.id)) {
                dismissedAds.push(currentAd.id);
                localStorage.setItem('dismissed_ads', JSON.stringify(dismissedAds));
            }
        }
    };

    const handleAdClick = () => {
        if (currentAd) {
            adsAPI.recordInteraction(currentAd.id, 'click');
        }
    };

    if (!currentAd || !isVisible) return null;

    if (currentAd.ad_type === 'popup') {
        return (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-300">
                <Card className="w-full max-w-lg overflow-hidden shadow-2xl border-primary/20">
                    <div className="relative">
                        {currentAd.image && (
                            <img
                                src={currentAd.image}
                                alt={currentAd.title}
                                className="w-full h-48 object-cover"
                            />
                        )}
                        <Button
                            variant="ghost"
                            size="icon"
                            className="absolute top-2 right-2 bg-black/20 hover:bg-black/40 text-white rounded-full"
                            onClick={handleClose}
                        >
                            <X className="h-5 w-5" />
                        </Button>
                    </div>
                    <CardHeader>
                        <div className="flex items-center space-x-2 text-primary mb-1">
                            <Info className="h-4 w-4" />
                            <span className="text-xs font-bold uppercase tracking-wider">Sponsorisé</span>
                        </div>
                        <CardTitle className="text-2xl">{currentAd.title}</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <p className="text-muted-foreground leading-relaxed">
                            {currentAd.description}
                        </p>

                        {currentAd.content && (
                            <div
                                className="prose prose-sm dark:prose-invert max-w-none"
                                dangerouslySetInnerHTML={{ __html: currentAd.content }}
                            />
                        )}

                        <div className="flex flex-col sm:flex-row gap-3 pt-2">
                            {currentAd.link_url && (
                                <Button asChild className="flex-1">
                                    <a href={currentAd.link_url} target="_blank" rel="noopener noreferrer" onClick={handleAdClick}>
                                        En savoir plus
                                        <ExternalLink className="ml-2 h-4 w-4" />
                                    </a>
                                </Button>
                            )}
                            {currentAd.contact_info && (
                                <Button variant="outline" className="flex-1">
                                    <Phone className="mr-2 h-4 w-4" />
                                    {currentAd.contact_info}
                                </Button>
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>
        );
    }

    if (currentAd.ad_type === 'notification') {
        return (
            <div className="fixed bottom-6 right-6 z-50 w-full max-w-sm animate-in slide-in-from-right duration-500">
                <Card className="shadow-xl border-primary/20 bg-card/95 backdrop-blur">
                    <CardContent className="p-4">
                        <div className="flex items-start space-x-4">
                            {currentAd.image ? (
                                <img
                                    src={currentAd.image}
                                    alt=""
                                    className="h-16 w-16 rounded-md object-cover flex-shrink-0"
                                />
                            ) : (
                                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                                    <Info className="h-6 w-6 text-primary" />
                                </div>
                            )}
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between mb-1">
                                    <span className="text-[10px] font-bold uppercase tracking-wider text-primary">Annonce</span>
                                    <button onClick={handleClose} className="text-muted-foreground hover:text-foreground">
                                        <X className="h-4 w-4" />
                                    </button>
                                </div>
                                <h4 className="font-semibold text-sm truncate">{currentAd.title}</h4>
                                <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
                                    {currentAd.description}
                                </p>
                                <div className="mt-3 flex items-center space-x-2">
                                    {currentAd.link_url && (
                                        <a
                                            href={currentAd.link_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-xs font-medium text-primary hover:underline flex items-center"
                                            onClick={handleAdClick}
                                        >
                                            Voir l'offre
                                            <ExternalLink className="ml-1 h-3 w-3" />
                                        </a>
                                    )}
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        );
    }

    if (currentAd.ad_type === 'banner') {
        return (
            <div className="fixed top-0 left-0 right-0 z-[100] animate-in slide-in-from-top duration-500">
                <div className="bg-primary text-primary-foreground px-4 py-3 shadow-lg">
                    <div className="container mx-auto flex items-center justify-between">
                        <div className="flex items-center space-x-4 overflow-hidden">
                            <Badge variant="outline" className="bg-white/20 text-white border-none shrink-0">Annonce</Badge>
                            <p className="text-sm font-medium truncate">
                                <span className="font-bold">{currentAd.title}:</span> {currentAd.description}
                            </p>
                        </div>
                        <div className="flex items-center space-x-4 shrink-0 ml-4">
                            {currentAd.link_url && (
                                <Button asChild size="sm" variant="secondary" className="h-8" onClick={handleAdClick}>
                                    <a href={currentAd.link_url} target="_blank" rel="noopener noreferrer">
                                        Découvrir
                                        <ExternalLink className="ml-2 h-3 w-3" />
                                    </a>
                                </Button>
                            )}
                            <button onClick={handleClose} className="hover:bg-white/20 p-1 rounded-full transition-colors">
                                <X className="h-4 w-4" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return null;
};

export default AdDisplay;

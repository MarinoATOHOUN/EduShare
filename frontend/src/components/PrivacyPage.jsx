/**
 * Privacy Policy Page Component
 * Developed by Marino ATOHOUN for BlackBenAI
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const PrivacyPage = () => {
    return (
        <div className="max-w-4xl mx-auto space-y-8 py-8">
            <div className="text-center space-y-2">
                <h1 className="text-4xl font-bold tracking-tight">Politique de Confidentialité</h1>
                <p className="text-muted-foreground">Dernière mise à jour : 27 décembre 2025</p>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>1. Introduction</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-muted-foreground">
                    <p>
                        Chez EduShare, opéré par <strong>BlackBenAI</strong>, nous accordons une importance capitale à la protection de vos données personnelles. Cette politique détaille comment nous collectons, utilisons et protégeons vos informations.
                    </p>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>2. Collecte des données</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-muted-foreground">
                    <p>
                        Nous collectons les informations suivantes :
                    </p>
                    <ul className="list-disc pl-6 space-y-2">
                        <li><strong>Informations de compte :</strong> Nom, prénom, adresse email et mot de passe (hashé).</li>
                        <li><strong>Informations de profil :</strong> Biographie, institution et préférences.</li>
                        <li><strong>Données d'utilisation :</strong> Historique des uploads, téléchargements et statistiques de consultation.</li>
                        <li><strong>Données techniques :</strong> Adresse IP, type de navigateur et cookies de session.</li>
                    </ul>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>3. Utilisation des données</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-muted-foreground">
                    <p>
                        Vos données sont utilisées pour :
                    </p>
                    <ul className="list-disc pl-6 space-y-2">
                        <li>Fournir et améliorer nos services de partage de documents.</li>
                        <li>Personnaliser votre expérience utilisateur.</li>
                        <li>Assurer la sécurité de votre compte et prévenir la fraude.</li>
                        <li>Vous contacter concernant des mises à jour importantes du service.</li>
                    </ul>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>4. Partage des données</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-muted-foreground">
                    <p>
                        <strong>BlackBenAI</strong> ne vend, n'échange, ni ne loue vos données personnelles à des tiers. Nous ne partageons des informations que dans les cas suivants :
                    </p>
                    <ul className="list-disc pl-6 space-y-2">
                        <li>Avec votre consentement explicite.</li>
                        <li>Pour nous conformer à des obligations légales.</li>
                        <li>Pour protéger les droits et la sécurité d'EduShare et de ses utilisateurs.</li>
                    </ul>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>5. Sécurité</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-muted-foreground">
                    <p>
                        Nous mettons en œuvre des mesures de sécurité techniques et organisationnelles pour protéger vos données contre tout accès non autorisé, modification ou destruction. Cependant, aucune méthode de transmission sur Internet n'est sûre à 100%.
                    </p>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>6. Vos droits</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-muted-foreground">
                    <p>
                        Conformément aux réglementations sur la protection des données, vous disposez d'un droit d'accès, de rectification, de suppression et d'opposition au traitement de vos données personnelles. Vous pouvez exercer ces droits depuis les paramètres de votre profil ou en nous contactant.
                    </p>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>7. Cookies</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-muted-foreground">
                    <p>
                        EduShare utilise des cookies pour maintenir votre session active et analyser l'utilisation du site. Vous pouvez configurer votre navigateur pour refuser les cookies, mais cela pourrait limiter certaines fonctionnalités.
                    </p>
                </CardContent>
            </Card>

            <div className="text-center text-sm text-muted-foreground py-4">
                <p>&copy; 2025 EduShare par BlackBenAI. Tous droits réservés.</p>
            </div>
        </div>
    );
};

export default PrivacyPage;

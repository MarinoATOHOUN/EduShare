/**
 * Terms of Service Page Component
 * Developed by Marino ATOHOUN for BlackBenAI
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import BlackBenAILink from './BlackBenAILink';

const TermsPage = () => {
    return (
        <div className="max-w-4xl mx-auto space-y-8 py-8">
            <div className="text-center space-y-2">
                <h1 className="text-4xl font-bold tracking-tight">Conditions Générales d'Utilisation</h1>
                <p className="text-muted-foreground">Dernière mise à jour : 27 décembre 2025</p>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>1. Acceptation des conditions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-muted-foreground">
                    <p>
                        En accédant et en utilisant EduShare, une plateforme créée par <BlackBenAILink />, vous acceptez d'être lié par les présentes conditions générales d'utilisation. Si vous n'acceptez pas ces conditions, veuillez ne pas utiliser nos services.
                    </p>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>2. Description du service</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-muted-foreground">
                    <p>
                        EduShare est une plateforme de partage de documents éducatifs au format PDF. Les utilisateurs peuvent uploader, prévisualiser et télécharger des ressources pédagogiques partagées par la communauté.
                    </p>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>3. Responsabilité de l'utilisateur</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-muted-foreground">
                    <p>
                        En tant qu'utilisateur, vous vous engagez à :
                    </p>
                    <ul className="list-disc pl-6 space-y-2">
                        <li>Ne partager que des contenus dont vous détenez les droits ou qui sont libres de droits.</li>
                        <li>Ne pas uploader de contenus illégaux, offensants ou inappropriés.</li>
                        <li>Respecter la propriété intellectuelle des autres contributeurs.</li>
                        <li>Maintenir la confidentialité de vos identifiants de connexion.</li>
                    </ul>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>4. Propriété intellectuelle</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-muted-foreground">
                    <p>
                        La plateforme EduShare, son design, son code et ses logos sont la propriété exclusive de <BlackBenAILink />. Les documents partagés restent la propriété de leurs auteurs respectifs, mais en les publiant sur EduShare, vous accordez à la plateforme une licence mondiale pour héberger et diffuser ces contenus.
                    </p>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>5. Limitation de responsabilité</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-muted-foreground">
                    <p>
                        <BlackBenAILink /> ne garantit pas l'exactitude ou la qualité des documents partagés par les utilisateurs. L'utilisation des ressources se fait sous la seule responsabilité de l'utilisateur. Nous ne pourrons être tenus responsables des dommages directs ou indirects résultant de l'utilisation du service.
                    </p>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>6. Modifications des conditions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-muted-foreground">
                    <p>
                        Nous nous réservons le droit de modifier ces conditions à tout moment. Les modifications prendront effet dès leur publication sur cette page.
                    </p>
                </CardContent>
            </Card>

            <div className="text-center text-sm text-muted-foreground py-4">
                <p>&copy; 2025 EduShare par <BlackBenAILink />. Tous droits réservés.</p>
            </div>
        </div>
    );
};

export default TermsPage;

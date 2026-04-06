/**
 * Pricing Page
 * Presents API plans and benefits for subscription.
 */

import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Check, KeyRound, Zap, Database, Shield, ArrowRight } from 'lucide-react';
import { developerAPI } from '../lib/api';

const formatPrice = (priceCents) => {
  if (!priceCents) return 'Gratuit';
  return `${(priceCents / 100).toFixed(2)} €`;
};

const PlanFeature = ({ children }) => (
  <div className="flex items-start gap-2 text-sm">
    <Check className="h-4 w-4 text-primary mt-0.5 shrink-0" />
    <span className="text-muted-foreground">{children}</span>
  </div>
);

const PricingPage = () => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const data = await developerAPI.getPlans();
        setPlans(Array.isArray(data) ? data : []);
      } catch {
        setPlans([]);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const freePlan = useMemo(() => plans.find((p) => p.code === 'free') || null, [plans]);
  const monthlyPlans = useMemo(() => plans.filter((p) => p.billing_period === 'monthly' && p.code !== 'free'), [plans]);
  const yearlyPlans = useMemo(() => plans.filter((p) => p.billing_period === 'yearly'), [plans]);

  const renderPlanCards = (list) => (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {freePlan && (
        <Card className="border-primary/20">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-xl">{freePlan.name}</CardTitle>
              <Badge variant="secondary">Découverte</Badge>
            </div>
            <CardDescription>{freePlan.description}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-3xl font-bold">{formatPrice(freePlan.price_cents)}</div>
              <div className="text-sm text-muted-foreground">Sans engagement</div>
            </div>

            <Separator />

            <div className="space-y-2">
              <PlanFeature>API key + endpoints “Data API”</PlanFeature>
              <PlanFeature>Filtres: domaine, niveau, tags, recherche</PlanFeature>
              <PlanFeature>
                Quotas: <strong>{freePlan.daily_requests_limit}</strong> requêtes/jour et{' '}
                <strong>{freePlan.daily_download_limit}</strong> téléchargements/jour
              </PlanFeature>
              <PlanFeature>Page max: <strong>{freePlan.max_page_size}</strong> items</PlanFeature>
              <PlanFeature>Suivi des quotas via <code>/api/data/whoami/</code></PlanFeature>
            </div>

            <div className="pt-2 flex gap-2">
              <Button asChild className="flex-1">
                <Link to="/developers">Générer une API key</Link>
              </Button>
              <Button asChild variant="outline">
                <Link to="/documents">Explorer</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {list.map((p) => (
        <Card key={p.code} className="border-primary/20">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-xl">{p.name}</CardTitle>
              <Badge variant="outline">API</Badge>
            </div>
            <CardDescription>{p.description}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-3xl font-bold">
                {formatPrice(p.price_cents)}
                <span className="text-sm text-muted-foreground font-normal">
                  {' '} / {p.billing_period === 'yearly' ? 'an' : 'mois'}
                </span>
              </div>
              <div className="text-sm text-muted-foreground">Accès API + quotas augmentés</div>
            </div>

            <Separator />

            <div className="space-y-2">
              <PlanFeature>
                Quotas: <strong>{p.daily_requests_limit}</strong> requêtes/jour
              </PlanFeature>
              <PlanFeature>
                Téléchargements: <strong>{p.daily_download_limit}</strong> / jour
              </PlanFeature>
              <PlanFeature>
                Page max: <strong>{p.max_page_size}</strong> items (meilleur débit)
              </PlanFeature>
              <PlanFeature>Extraction en volume via pagination + <code>download_url</code></PlanFeature>
              <PlanFeature>Gestion des clés (création / révocation) depuis la plateforme</PlanFeature>
            </div>

            <div className="pt-2 flex gap-2">
              <Button asChild className="flex-1">
                <Link to="/developers">Commencer</Link>
              </Button>
              <Button asChild variant="outline">
                <Link to="/developers">Docs API</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto space-y-10 py-8">
      <section className="text-center space-y-4">
        <div className="flex justify-center">
          <Badge variant="secondary" className="gap-2">
            <KeyRound className="h-4 w-4" />
            API EduShare
          </Badge>
        </div>
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight">Offres & Tarification</h1>
        <p className="text-muted-foreground max-w-3xl mx-auto">
          Accède à une base de données éducative en croissance via API Key. Les offres débloquent des quotas plus élevés
          pour télécharger des cours en grande quantité.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
          <Button asChild size="lg">
            <Link to="/developers" className="flex items-center gap-2">
              Ouvrir l’espace développeur <ArrowRight className="h-5 w-5" />
            </Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <Link to="/documents">Voir les cours</Link>
          </Button>
        </div>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <Database className="h-8 w-8 text-primary mb-2" />
            <CardTitle>Extraction en volume</CardTitle>
            <CardDescription>
              Liste paginée + filtres (domaines, niveaux, tags) pour construire ta base de données.
            </CardDescription>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <Zap className="h-8 w-8 text-primary mb-2" />
            <CardTitle>Débit contrôlé</CardTitle>
            <CardDescription>
              Les offres augmentent les quotas et la taille de page maximale pour accélérer tes exports.
            </CardDescription>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <Shield className="h-8 w-8 text-primary mb-2" />
            <CardTitle>Clés sécurisées</CardTitle>
            <CardDescription>
              Les API keys sont hashées côté serveur, révocables à tout moment, et suivies par quotas/jour.
            </CardDescription>
          </CardHeader>
        </Card>
      </section>

      <section className="space-y-4">
        <div className="flex items-end justify-between gap-4 flex-wrap">
          <div className="space-y-1">
            <h2 className="text-3xl font-bold">Choisis ton rythme</h2>
            <p className="text-muted-foreground">Mensuel ou Annuel (si disponible).</p>
          </div>
          <Button asChild variant="outline">
            <Link to="/developers">Voir la doc technique</Link>
          </Button>
        </div>

        <Card>
          <CardContent className="pt-6">
            {loading ? (
              <p className="text-sm text-muted-foreground">Chargement des offres…</p>
            ) : plans.length === 0 ? (
              <p className="text-sm text-muted-foreground">Aucune offre disponible.</p>
            ) : (
              <Tabs defaultValue="monthly" className="w-full">
                <TabsList>
                  <TabsTrigger value="monthly">Mensuel</TabsTrigger>
                  <TabsTrigger value="yearly">Annuel</TabsTrigger>
                </TabsList>
                <TabsContent value="monthly" className="pt-6">
                  {renderPlanCards(monthlyPlans)}
                </TabsContent>
                <TabsContent value="yearly" className="pt-6">
                  {renderPlanCards(yearlyPlans)}
                </TabsContent>
              </Tabs>
            )}
          </CardContent>
        </Card>
      </section>

      <section className="space-y-4">
        <h2 className="text-3xl font-bold">FAQ</h2>
        <Accordion type="multiple" className="w-full">
          <AccordionItem value="q1">
            <AccordionTrigger>Comment je récupère ma clé API ?</AccordionTrigger>
            <AccordionContent className="text-muted-foreground">
              Va sur <Link to="/developers" className="text-primary underline">/developers</Link>, crée une API key et copie-la.
              Elle est affichée une seule fois.
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="q2">
            <AccordionTrigger>Comment je télécharge beaucoup de cours ?</AccordionTrigger>
            <AccordionContent className="text-muted-foreground">
              Utilise <code>/api/data/documents/</code> avec pagination (<code>page</code>, <code>page_size</code>) puis
              télécharge via <code>download_url</code>. Les offres augmentent les quotas/jour et la taille de page max.
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="q3">
            <AccordionTrigger>Que se passe-t-il si je dépasse le quota ?</AccordionTrigger>
            <AccordionContent className="text-muted-foreground">
              L’API renvoie <code>429</code>. Tu peux vérifier tes compteurs via <code>/api/data/whoami/</code>.
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="q4">
            <AccordionTrigger>Est-ce que le paiement est déjà intégré ?</AccordionTrigger>
            <AccordionContent className="text-muted-foreground">
              Les offres et quotas sont prêts. L’activation d’une offre peut être gérée côté admin pour l’instant
              (intégration Stripe/PayPal possible ensuite).
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </section>
    </div>
  );
};

export default PricingPage;

